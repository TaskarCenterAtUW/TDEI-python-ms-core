import json
import logging
import time
from .config.topic_config import Config
from ..resource_errors import ExceptionHandler
from concurrent.futures import ThreadPoolExecutor
from .abstract.topic_abstract import TopicAbstract
from ..queue.models.queue_message import QueueMessage

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('Topic')
logger.setLevel(logging.INFO)


class Callback:
    def __init__(self, fn=None, max_concurrent_messages=1):
        self._function_to_call = fn
        self._max_concurrent_messages = max_concurrent_messages
        self._renewal_interval = 30  # seconds
        self.message_processing = 0
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_messages)

    def _renew_message_lock(self, message, receiver):
        while True:
            try:
                time.sleep(self._renewal_interval)
                if not message._lock_expired:
                    receiver.renew_message_lock(message)
            except Exception as e:
                break

    # Sends data to the callback function
    def process_message(self, message, receiver):
        queue_message = QueueMessage.data_from(str(message))
        secondary_executor = ThreadPoolExecutor(max_workers=1)
        if not message._lock_expired:
            secondary_executor.submit(self._renew_message_lock, message, receiver)
        self._function_to_call(queue_message)

    # Starts listening to the messages
    def start_listening(self, provider, topic, subscription):
        with provider.client:  # service bus client
            logger.info('Initiating receiver')
            topic_receiver = provider.client.get_subscription_receiver(
                topic_name=topic,
                subscription_name=subscription
            )
            logger.info('Receiver started')
            with topic_receiver:
                while True:
                    available_slots = self._max_concurrent_messages - self.message_processing
                    if available_slots > 0:
                        try:
                            messages = topic_receiver.receive_messages(
                                max_message_count=available_slots,
                                max_wait_time=5
                            )
                            if not messages:
                                continue
                            for message in messages:
                                self.message_processing += 1
                                self.executor.submit(self._process_message_in_thread, message, topic_receiver)
                        except Exception as et:
                            logger.error(f'Error in service bus connection: {et}')
                    else:
                        time.sleep(10)  # Short sleep to prevent tight loop if no slots available

                logger.info('Receiver stopped')

    def _process_message_in_thread(self, message, topic_receiver):
        try:
            self.process_message(message=message, receiver=topic_receiver)
        except Exception as e:
            logger.error(f'Error: {e}, Invalid message received: {message}')
        finally:
            try:
                topic_receiver.complete_message(message)  # Mark the message as complete
            except Exception as err:
                logger.error(f'Error completing the message: {err}')
            self.message_processing -= 1


class Topic(TopicAbstract):
    def __init__(self, config=None, topic_name=None, max_concurrent_messages=1):
        self.topic = topic_name
        self.provider = Config(config=config, topic_name=topic_name)
        self.max_concurrent_messages = max_concurrent_messages

    @ExceptionHandler.decorated
    def subscribe(self, subscription=None, callback=None):
        if subscription is not None:
            cb = Callback(callback, max_concurrent_messages=self.max_concurrent_messages)
            cb.start_listening(self.provider, self.topic, subscription)
        else:
            logging.error(
                f'Unimplemented initialize for core {self.provider.provider}, Subscription name is required!')

    @ExceptionHandler.decorated
    def publish(self, data=None):
        message = QueueMessage.to_dict(data)
        with self.provider.client:
            sender = self.provider.client.get_topic_sender(topic_name=self.provider.topic)
            with sender:
                sender.send_messages(self.provider.sender(json.dumps(message)))
