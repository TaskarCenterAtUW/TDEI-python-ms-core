import datetime
import json
import logging
import multiprocessing as mp
import os
import time
import traceback
from ..config.config import TopicConfig
from concurrent.futures import ThreadPoolExecutor
from .abstract.topic_abstract import TopicAbstract
from ..queue.models.queue_message import QueueMessage
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus import AutoLockRenewer
import threading


logger = logging.getLogger('AzureTopic')


"""
AzureTopic class represents a topic in Azure Service Bus.
Attributes:
    topic (str): The name of the topic.
    client (ServiceBusClient): The ServiceBusClient object used to interact with the Service Bus.
    max_concurrent_messages (int): The maximum number of concurrent messages to process.
    topic_name (str): The name of the topic.
    publisher (TopicSender): The TopicSender object used to send messages to the topic.
    executor (ThreadPoolExecutor): The ThreadPoolExecutor object used to execute callback functions.
    internal_count (int): The internal count of concurrent messages being processed.
    lock_renewal (AutoLockRenewer): The AutoLockRenewer object used to renew message locks.
    max_renewal_duration (int): The maximum duration in seconds to renew a message lock.
    wait_time_for_message (int): The maximum wait time in seconds to receive messages.
Methods:
    publish(data: QueueMessage) -> None:
        Publishes a message to the topic.
    subscribe(subscription: str, callback) -> None:
        Subscribes to a subscription of the topic and processes incoming messages.
    internal_callback(message, callbackfn) -> ServiceBusMessage:
        Internal callback function that processes a message and invokes the callback function.
    settle_message(x: cf.Future) -> None:
        Sets the message as completed and updates the internal count.
"""
class AzureTopic(TopicAbstract):
    def __init__(self, config: TopicConfig=None, topic_name=None, max_concurrent_messages:int=1):
        self.topic = topic_name
        self.client = ServiceBusClient.from_connection_string(conn_str=config.connection_string, retry_total=10, retry_backoff_factor=1, retry_backoff_max=30)
        self.max_concurrent_messages = max_concurrent_messages
        self.topic_name = topic_name
        self.publisher = self.client.get_topic_sender(topic_name=topic_name)
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_messages)
        self.callback_execution_mode = self._get_callback_execution_mode()
        self.callback_process_fallback_mode = self._get_process_fallback_mode()
        self.callback_process_start_method = self._get_process_start_method()
        self.process_context = self._get_process_context()
        self.internal_count = 0
        self.max_renewal_duration = 86400  # Renew the message upto 1 day
        self.lock_renewal_margin = 60
        renewer_max_workers = max(max_concurrent_messages, 2)
        self.lock_renewal = AutoLockRenewer(
            max_lock_renewal_duration=self.max_renewal_duration,
            on_lock_renew_failure=self._handle_lock_renew_failure,
            max_workers=renewer_max_workers,
        )
        # The SDK default renews only in the last 10 seconds of the lock window.
        # Start earlier so long-running jobs have more headroom for scheduler jitter.
        self.lock_renewal._renew_period = min(self.lock_renewal_margin, self.max_renewal_duration)
        self.wait_time_for_message = 5
        self.thread_lock = threading.Lock()
        self.pending_tasks = []
        self.inflight_tasks = {}
        self.inflight_lock_renewal_state = {}
        self.lock_renew_retry_interval = 5
    
    
    def publish(self, data: QueueMessage):
        """
        Publishes a message to the topic.
        Args:
            data (QueueMessage): The message to publish.
        
        """
        message = QueueMessage.to_dict(data)
        self.publisher.send_messages(ServiceBusMessage(json.dumps(message)))

    def subscribe(self, subscription: str, callback, max_receivable_messages=-1):

        """
        Subscribes to a subscription of the topic and processes incoming messages.
        Args:
            subscription (str): The name of the subscription to subscribe to.
            callback (function): The callback function to invoke for each message.
        """
        self.receiver = self.client.get_subscription_receiver(topic_name=self.topic_name, subscription_name=subscription)
        self.receiver.local_received_messages = 0
        while True:
                try:
                    self._renew_inflight_message_locks()
                    self._settle_completed_tasks()
                    to_receive = self._get_receivable_count(max_receivable_messages=max_receivable_messages)
                    if max_receivable_messages > 0 and self.receiver.local_received_messages >= max_receivable_messages:
                        if len(self.pending_tasks) == 0:
                            break
                        self._wait_for_pending_tasks(timeout=0.5)
                        continue
                    if to_receive > 0:
                        messages = self.receiver.receive_messages(max_message_count=to_receive, max_wait_time=self.wait_time_for_message)
                        if not messages or len(messages) == 0:
                            if len(self.pending_tasks) > 0:
                                self._wait_for_pending_tasks(timeout=0.5)
                            continue
                        self.receiver.local_received_messages += len(messages)
                        with self.thread_lock:
                            self.internal_count += len(messages)
                        for message in messages: 
                            self.lock_renewal.register(
                                self.receiver,
                                message,
                                max_lock_renewal_duration=self.max_renewal_duration,
                                on_lock_renew_failure=self._handle_lock_renew_failure,
                            )
                            execution_task = self._submit_processing_task(message, callback)
                            self._track_inflight_task(message, execution_task)
                            self.pending_tasks.append((execution_task, message))
                    else:
                        if len(self.pending_tasks) > 0:
                            self._wait_for_pending_tasks(timeout=0.5)
                        else:
                            time.sleep(self.wait_time_for_message)
                except Exception as e:
                    logger.error(f'Error in receiving messages: {e}')

    
    def internal_callback(self, message_payload, callbackfn):
        """
        Internal callback function that processes a message and invokes the callback function.
        Args:
            message_payload (str): The message payload to process.
            callbackfn (function): The callback function to invoke.
        Returns:
            dict: The callback status payload.
        """
        try:
            queue_message = QueueMessage.data_from(message_payload)
            callbackfn(queue_message)
            return {'success': True, 'error': None}
        except Exception as e:
            return {
                'success': False,
                'error': ''.join(traceback.format_exception(type(e), e, e.__traceback__)).strip(),
            }
                             
    
    def settle_message(self, x):
        return self._settle_task(x)

    def _submit_processing_task(self, message, callback):
        message_payload = str(message)
        if self.callback_execution_mode == 'process':
            try:
                return self._submit_process_task(message_payload, callback)
            except Exception as exc:
                message_id = self._get_message_id(message)
                if self.callback_process_fallback_mode == 'thread':
                    logger.warning(
                        'Falling back to thread execution for message %s because process start failed: %s',
                        message_id,
                        exc,
                    )
                    return self._submit_thread_task(message_payload, callback)
                logger.error(
                    'Process execution failed for message %s and thread fallback is disabled: %s',
                    message_id,
                    exc,
                )
                return _ImmediateExecutionTask({
                    'success': False,
                    'error': f'Process execution failed and thread fallback is disabled: {exc}',
                })
        return self._submit_thread_task(message_payload, callback)

    def _submit_thread_task(self, message_payload, callback):
        future = self.executor.submit(self.internal_callback, message_payload, callback)
        return _FutureExecutionTask(future)

    def _submit_process_task(self, message_payload, callback):
        if self.process_context is None:
            raise RuntimeError('Process execution mode is not available for this environment.')

        parent_connection, child_connection = self.process_context.Pipe(duplex=False)
        callback_process = self.process_context.Process(
            target=_run_callback_in_subprocess,
            args=(message_payload, callback, child_connection),
        )
        try:
            callback_process.start()
        except Exception:
            parent_connection.close()
            child_connection.close()
            raise
        child_connection.close()
        return _ProcessExecutionTask(callback_process, parent_connection)

    def _get_receivable_count(self, max_receivable_messages=-1):
        with self.thread_lock:
            available_slots = self.max_concurrent_messages - self.internal_count
        if max_receivable_messages > 0:
            remaining_messages = max_receivable_messages - self.receiver.local_received_messages
            available_slots = min(available_slots, remaining_messages)
        return max(available_slots, 0)

    def _wait_for_pending_tasks(self, timeout=0.5):
        if len(self.pending_tasks) == 0:
            return
        if timeout <= 0:
            self._settle_completed_tasks()
            return
        deadline = time.time() + timeout
        while time.time() < deadline:
            self._renew_inflight_message_locks()
            if any(task.done() for task, _ in self.pending_tasks):
                break
            time.sleep(min(0.1, max(deadline - time.time(), 0)))
        self._renew_inflight_message_locks()
        self._settle_completed_tasks()

    def _settle_completed_tasks(self):
        remaining_tasks = []
        for future, incoming_message in self.pending_tasks:
            if future.done():
                self._settle_task(future, incoming_message=incoming_message)
            else:
                remaining_tasks.append((future, incoming_message))
        self.pending_tasks = remaining_tasks

    def _settle_task(self, x, incoming_message=None):
        """
        Sets the message as completed and updates the internal count.
        Args:
            x: The task object representing the message processing.
        """
        try:
            task_result = x.result()
        except Exception as e:
            task_result = {
                'success': False,
                'error': f'Callback worker exited before returning a result: {e}',
            }

        try:
            if incoming_message is None:
                return
            if getattr(incoming_message, '_lock_expired', False):
                logger.error(
                    f'Skipping settlement for message {self._get_message_id(incoming_message)} '
                    f'because the lock expired at {getattr(incoming_message, "locked_until_utc", None)}. '
                    f'auto_renew_error={getattr(incoming_message, "auto_renew_error", None)}'
                )
                return
            if task_result.get('success'):
                self.receiver.complete_message(incoming_message)
            else:
                logger.error(
                    'Processing failed for message %s: %s',
                    self._get_message_id(incoming_message),
                    task_result.get('error', 'unknown processing failure'),
                )
                self.receiver.abandon_message(incoming_message)
        except Exception as e:
            logger.error(f'Error in settling message: {e}')
        finally:
            if incoming_message is not None:
                self._release_inflight_task(incoming_message)
            with self.thread_lock:
                self.internal_count = max(self.internal_count - 1, 0)
        return

    def _handle_lock_renew_failure(self, renewable, error):
        message_id = self._get_message_id(renewable)
        failure_reason = error or getattr(renewable, 'auto_renew_error', None) or 'lock expired before renewal could complete'
        logger.error(
            f'Error renewing lock for message {message_id}: {failure_reason}; '
            f'locked_until_utc={getattr(renewable, "locked_until_utc", None)}'
        )
        if getattr(renewable, '_lock_expired', False):
            self._cancel_inflight_task(
                renewable,
                f'message lock expired after renewal failure: {failure_reason}',
            )

    def _track_inflight_task(self, message, task):
        with self.thread_lock:
            message_key = self._get_message_key(message)
            self.inflight_tasks[message_key] = task
            self.inflight_lock_renewal_state[message_key] = {
                'message': message,
                'renew_margin': self._get_lock_renewal_margin_seconds(message),
                'last_renew_attempt': 0,
            }

    def _release_inflight_task(self, message):
        with self.thread_lock:
            message_key = self._get_message_key(message)
            self.inflight_tasks.pop(message_key, None)
            self.inflight_lock_renewal_state.pop(message_key, None)

    def _renew_inflight_message_locks(self):
        with self.thread_lock:
            renewal_items = [
                (
                    message_key,
                    state['message'],
                    self.inflight_tasks.get(message_key),
                    state['renew_margin'],
                    state['last_renew_attempt'],
                )
                for message_key, state in self.inflight_lock_renewal_state.items()
            ]

        for message_key, message, task, renew_margin, last_renew_attempt in renewal_items:
            if task is None or task.done():
                continue
            if getattr(message, '_lock_expired', False):
                self._handle_lock_renew_failure(message, getattr(message, 'auto_renew_error', None))
                continue

            locked_until_utc = getattr(message, 'locked_until_utc', None)
            if locked_until_utc is None:
                continue

            remaining_seconds = (locked_until_utc - self._utc_now_for(locked_until_utc)).total_seconds()
            if remaining_seconds > renew_margin:
                continue

            current_time = time.time()
            if current_time - last_renew_attempt < self.lock_renew_retry_interval:
                continue

            with self.thread_lock:
                state = self.inflight_lock_renewal_state.get(message_key)
                if state is None:
                    continue
                state['last_renew_attempt'] = current_time

            try:
                renewed_until = self.receiver.renew_message_lock(message)
                logger.info(
                    'Renewed lock for message %s until %s',
                    self._get_message_id(message),
                    renewed_until,
                )
            except Exception as exc:
                message.auto_renew_error = exc
                logger.error(
                    'Error proactively renewing lock for message %s: %s; locked_until_utc=%s',
                    self._get_message_id(message),
                    exc,
                    getattr(message, 'locked_until_utc', None),
                )
                if getattr(message, '_lock_expired', False):
                    self._handle_lock_renew_failure(message, exc)

    def _get_lock_renewal_margin_seconds(self, message):
        locked_until_utc = getattr(message, 'locked_until_utc', None)
        received_timestamp_utc = getattr(message, '_received_timestamp_utc', None)
        if (
            isinstance(locked_until_utc, datetime.datetime)
            and isinstance(received_timestamp_utc, datetime.datetime)
        ):
            lock_duration_seconds = (locked_until_utc - received_timestamp_utc).total_seconds()
            if lock_duration_seconds > 0:
                return max(5, min(self.lock_renewal_margin, lock_duration_seconds * 0.5))
        return min(self.lock_renewal_margin, 30)

    def _cancel_inflight_task(self, message, reason):
        with self.thread_lock:
            task = self.inflight_tasks.get(self._get_message_key(message))
        if task is None or task.done():
            return
        message_id = self._get_message_id(message)
        if task.cancel(reason):
            logger.error(
                'Cancelled callback worker for message %s because %s',
                message_id,
                reason,
            )
        else:
            logger.error(
                'Unable to cancel callback worker for message %s after %s',
                message_id,
                reason,
            )

    @staticmethod
    def _get_message_id(message):
        return getattr(message, 'message_id', None) or getattr(message, 'messageId', 'unknown')

    @staticmethod
    def _get_message_key(message):
        return id(message)

    @staticmethod
    def _utc_now_for(value):
        now = datetime.datetime.now(datetime.timezone.utc)
        if getattr(value, 'tzinfo', None) is None:
            return now.replace(tzinfo=None)
        return now

    @staticmethod
    def _get_callback_execution_mode():
        value = os.environ.get('TOPIC_CALLBACK_EXECUTION_MODE', 'process')
        normalized = str(value).strip().lower()
        if normalized in ('process', 'thread'):
            return normalized
        logger.warning(
            'Invalid value for TOPIC_CALLBACK_EXECUTION_MODE: %s. Using default process.',
            value,
        )
        return 'process'

    @staticmethod
    def _get_process_fallback_mode():
        value = os.environ.get('TOPIC_CALLBACK_PROCESS_FALLBACK_MODE', 'thread')
        normalized = str(value).strip().lower()
        if normalized in ('error', 'thread'):
            return normalized
        logger.warning(
            'Invalid value for TOPIC_CALLBACK_PROCESS_FALLBACK_MODE: %s. Using thread.',
            value,
        )
        return 'thread'

    @staticmethod
    def _get_process_start_method():
        available_methods = mp.get_all_start_methods()
        default_method = 'fork' if 'fork' in available_methods else mp.get_start_method() or available_methods[0]
        configured_method = os.environ.get('TOPIC_CALLBACK_PROCESS_START_METHOD', default_method)
        normalized_method = str(configured_method).strip().lower()
        if normalized_method in available_methods:
            return normalized_method
        logger.warning(
            'Invalid value for TOPIC_CALLBACK_PROCESS_START_METHOD: %s. Using default %s.',
            configured_method,
            default_method,
        )
        return default_method

    def _get_process_context(self):
        if self.callback_execution_mode != 'process':
            return None
        try:
            return mp.get_context(self.callback_process_start_method)
        except ValueError:
            logger.warning(
                'Process start method %s is unavailable. Falling back to thread execution.',
                self.callback_process_start_method,
            )
            self.callback_execution_mode = 'thread'
            return None


def _run_callback_in_subprocess(message_payload, callbackfn, result_connection):
    try:
        queue_message = QueueMessage.data_from(message_payload)
        callbackfn(queue_message)
        result_connection.send({'success': True, 'error': None})
    except BaseException as exc:  # pragma: no cover - exercised through the parent process wrapper
        result_connection.send({
            'success': False,
            'error': ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)).strip(),
        })
    finally:
        result_connection.close()


class _ImmediateExecutionTask:
    def __init__(self, result):
        self._result = result

    def done(self):
        return True

    def result(self):
        return self._result

    def cancel(self, reason):
        return False


class _FutureExecutionTask:
    def __init__(self, future):
        self._future = future

    def done(self):
        return self._future.done()

    def result(self):
        return self._future.result()

    def cancel(self, reason):
        return self._future.cancel()


class _ProcessExecutionTask:
    def __init__(self, process, result_connection):
        self._process = process
        self._result_connection = result_connection
        self._result = None
        self._connection_closed = False

    def done(self):
        return self._result is not None or not self._process.is_alive()

    def result(self):
        if self._result is not None:
            return self._result

        self._process.join()
        try:
            if self._result_connection.poll():
                self._result = self._result_connection.recv()
            else:
                self._result = {
                    'success': False,
                    'error': f'Callback worker exited with code {self._process.exitcode} without returning a result.',
                }
        finally:
            self._close_result_connection()

        return self._result

    def cancel(self, reason):
        if self.done():
            return False

        self._process.terminate()
        self._process.join(timeout=5)
        if self._process.is_alive() and hasattr(self._process, 'kill'):
            self._process.kill()
            self._process.join(timeout=5)

        self._result = {
            'success': False,
            'error': f'Callback worker terminated because {reason}.',
        }
        self._close_result_connection()
        return True

    def _close_result_connection(self):
        if self._connection_closed:
            return
        self._connection_closed = True
        self._result_connection.close()
