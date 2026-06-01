import datetime
import os
import unittest
from unittest.mock import MagicMock, patch

from src.python_ms_core.core.topic.azure_topic import AzureTopic


class CompletedTask:
    def __init__(self, result=None, error=None):
        self._result = result
        self._error = error

    def done(self):
        return True

    def result(self):
        if self._error is not None:
            raise self._error
        return self._result


class TestAzureTopic(unittest.TestCase):

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_init_sets_process_execution_defaults(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_renewer = MagicMock()
        mock_process_context = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_auto_lock_renewer.return_value = mock_renewer
        mock_get_context.return_value = mock_process_context

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)

        self.assertEqual(topic.callback_execution_mode, 'process')
        self.assertEqual(topic.callback_process_fallback_mode, 'thread')
        self.assertEqual(topic.callback_process_start_method, 'fork')
        self.assertIs(topic.process_context, mock_process_context)
        mock_auto_lock_renewer.assert_called_once()
        _, kwargs = mock_auto_lock_renewer.call_args
        self.assertEqual(kwargs['max_lock_renewal_duration'], 86400)
        self.assertEqual(kwargs['max_workers'], 2)
        self.assertEqual(mock_renewer._renew_period, 60)
        mock_get_context.assert_called_once_with('fork')

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_submit_processing_task_uses_process_runner_by_default(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message = MagicMock()
        mock_callback = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_get_context.return_value = MagicMock()
        mock_message.__str__.return_value = '{"message":"hello"}'

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic._submit_process_task = MagicMock(return_value='process-task')
        topic._submit_thread_task = MagicMock(return_value='thread-task')

        task = topic._submit_processing_task(mock_message, mock_callback)

        self.assertEqual(task, 'process-task')
        topic._submit_process_task.assert_called_once_with('{"message":"hello"}', mock_callback)
        topic._submit_thread_task.assert_not_called()

    @patch.dict(os.environ, {'TOPIC_CALLBACK_PROCESS_FALLBACK_MODE': 'thread'}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_submit_processing_task_falls_back_to_thread_when_process_start_fails(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message = MagicMock()
        mock_callback = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_get_context.return_value = MagicMock()
        mock_message.message_id = 'message-1'
        mock_message.__str__.return_value = '{"message":"hello"}'

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic._submit_process_task = MagicMock(side_effect=RuntimeError('process boom'))
        topic._submit_thread_task = MagicMock(return_value='thread-task')

        task = topic._submit_processing_task(mock_message, mock_callback)

        self.assertEqual(task, 'thread-task')
        topic._submit_thread_task.assert_called_once_with('{"message":"hello"}', mock_callback)
        mock_logger.warning.assert_called_once()
        warning_args = mock_logger.warning.call_args[0]
        self.assertEqual(
            warning_args[0],
            'Falling back to thread execution for message %s because process start failed: %s',
        )
        self.assertEqual(warning_args[1], 'message-1')
        self.assertEqual(str(warning_args[2]), 'process boom')

    @patch.dict(os.environ, {'TOPIC_CALLBACK_PROCESS_FALLBACK_MODE': 'error'}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_submit_processing_task_returns_failure_when_process_fails_and_thread_fallback_disabled(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message = MagicMock()
        mock_callback = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_get_context.return_value = MagicMock()
        mock_message.message_id = 'message-1'
        mock_message.__str__.return_value = '{"message":"hello"}'

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic._submit_process_task = MagicMock(side_effect=RuntimeError('process boom'))
        topic._submit_thread_task = MagicMock(return_value='thread-task')

        task = topic._submit_processing_task(mock_message, mock_callback)

        self.assertTrue(task.done())
        self.assertEqual(
            task.result(),
            {
                'success': False,
                'error': 'Process execution failed and thread fallback is disabled: process boom',
            },
        )
        topic._submit_thread_task.assert_not_called()
        mock_logger.error.assert_called_once()
        error_args = mock_logger.error.call_args[0]
        self.assertEqual(
            error_args[0],
            'Process execution failed for message %s and thread fallback is disabled: %s',
        )
        self.assertEqual(error_args[1], 'message-1')
        self.assertEqual(str(error_args[2]), 'process boom')

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_subscribe_settles_completed_tasks_on_receiver_loop(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
    ):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message._lock_expired = False

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_client.get_subscription_receiver.return_value = mock_receiver
        mock_receiver.receive_messages.side_effect = [[mock_message]]
        mock_get_context.return_value = MagicMock()

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        callback = MagicMock()
        topic._submit_processing_task = MagicMock(
            return_value=CompletedTask({'success': True, 'error': None})
        )

        topic.subscribe(subscription='mock-subscription', callback=callback, max_receivable_messages=1)

        topic._submit_processing_task.assert_called_once_with(mock_message, callback)
        mock_auto_lock_renewer.return_value.register.assert_called_once_with(
            mock_receiver,
            mock_message,
            max_lock_renewal_duration=topic.max_renewal_duration,
            on_lock_renew_failure=topic._handle_lock_renew_failure,
        )
        mock_receiver.complete_message.assert_called_once_with(mock_message)
        mock_receiver.abandon_message.assert_not_called()

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_settle_task_abandons_message_when_worker_reports_failure(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')

        mock_message._lock_expired = False
        mock_message.message_id = 'message-1'
        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_client.get_subscription_receiver.return_value = mock_receiver
        mock_get_context.return_value = MagicMock()

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic.receiver = mock_receiver
        topic.internal_count = 1

        topic._settle_task(
            CompletedTask({'success': False, 'error': 'worker failure'}),
            incoming_message=mock_message,
        )

        mock_receiver.complete_message.assert_not_called()
        mock_receiver.abandon_message.assert_called_once_with(mock_message)
        mock_logger.error.assert_called_once_with(
            'Processing failed for message %s: %s',
            'message-1',
            'worker failure',
        )
        self.assertEqual(topic.internal_count, 0)

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_settle_task_abandons_message_when_worker_exits_without_result(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')

        mock_message._lock_expired = False
        mock_message.message_id = 'message-2'
        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_client.get_subscription_receiver.return_value = mock_receiver
        mock_get_context.return_value = MagicMock()

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic.receiver = mock_receiver
        topic.internal_count = 1

        topic._settle_task(
            CompletedTask(error=RuntimeError('worker died')),
            incoming_message=mock_message,
        )

        mock_receiver.complete_message.assert_not_called()
        mock_receiver.abandon_message.assert_called_once_with(mock_message)
        mock_logger.error.assert_called_once_with(
            'Processing failed for message %s: %s',
            'message-2',
            'Callback worker exited before returning a result: worker died',
        )
        self.assertEqual(topic.internal_count, 0)

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_settle_task_logs_error_and_releases_slot(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')

        mock_message._lock_expired = False
        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_client.get_subscription_receiver.return_value = mock_receiver
        mock_receiver.complete_message.side_effect = Exception('Mocked settlement failure')
        mock_get_context.return_value = MagicMock()

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic.receiver = mock_receiver
        topic.internal_count = 1

        topic._settle_task(
            CompletedTask({'success': True, 'error': None}),
            incoming_message=mock_message,
        )

        mock_receiver.complete_message.assert_called_once_with(mock_message)
        mock_logger.error.assert_called_once_with('Error in settling message: Mocked settlement failure')
        self.assertEqual(topic.internal_count, 0)

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_settle_task_skips_expired_message(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')

        mock_message._lock_expired = True
        mock_message.message_id = 'message-1'
        mock_message.locked_until_utc = '2026-03-17T09:39:28Z'
        mock_message.auto_renew_error = None
        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_client.get_subscription_receiver.return_value = mock_receiver
        mock_get_context.return_value = MagicMock()

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic.receiver = mock_receiver
        topic.internal_count = 1

        topic._settle_task(
            CompletedTask({'success': True, 'error': None}),
            incoming_message=mock_message,
        )

        mock_receiver.complete_message.assert_not_called()
        mock_receiver.abandon_message.assert_not_called()
        mock_logger.error.assert_called_once_with(
            'Skipping settlement for message message-1 because the lock expired at '
            '2026-03-17T09:39:28Z. auto_renew_error=None'
        )
        self.assertEqual(topic.internal_count, 0)

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_handle_lock_renew_failure_cancels_running_inflight_task(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message = MagicMock()
        mock_task = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_get_context.return_value = MagicMock()
        mock_message.message_id = 'message-1'
        mock_message.locked_until_utc = '2026-03-17T09:39:28Z'
        mock_message._lock_expired = True
        mock_task.done.return_value = False
        mock_task.cancel.return_value = True

        topic = AzureTopic(config=mock_config, topic_name='mock-topic')
        topic._track_inflight_task(mock_message, mock_task)

        topic._handle_lock_renew_failure(mock_message, RuntimeError('renew failed'))

        mock_task.cancel.assert_called_once_with('message lock expired after renewal failure: renew failed')
        self.assertEqual(mock_logger.error.call_count, 2)
        self.assertEqual(
            mock_logger.error.call_args_list[1][0],
            (
                'Cancelled callback worker for message %s because %s',
                'message-1',
                'message lock expired after renewal failure: renew failed',
            ),
        )

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_handle_lock_renew_failure_does_not_cancel_when_lock_is_still_active(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message = MagicMock()
        mock_task = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_get_context.return_value = MagicMock()
        mock_message.message_id = 'message-1'
        mock_message.locked_until_utc = '2026-03-17T09:39:28Z'
        mock_message._lock_expired = False
        mock_task.done.return_value = False

        topic = AzureTopic(config=mock_config, topic_name='mock-topic')
        topic._track_inflight_task(mock_message, mock_task)

        topic._handle_lock_renew_failure(mock_message, RuntimeError('renew failed'))

        mock_task.cancel.assert_not_called()
        mock_logger.error.assert_called_once_with(
            'Error renewing lock for message message-1: renew failed; '
            'locked_until_utc=2026-03-17T09:39:28Z'
        )

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_renew_inflight_message_locks_renews_before_expiration(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        now = datetime.datetime.now(datetime.timezone.utc)
        renewed_until = now + datetime.timedelta(seconds=45)
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message = MagicMock()
        mock_task = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_get_context.return_value = MagicMock()
        mock_message.message_id = 'message-1'
        mock_message._lock_expired = False
        mock_message._received_timestamp_utc = now - datetime.timedelta(seconds=20)
        mock_message.locked_until_utc = now + datetime.timedelta(seconds=10)
        mock_task.done.return_value = False
        mock_receiver.renew_message_lock.return_value = renewed_until

        topic = AzureTopic(config=mock_config, topic_name='mock-topic')
        topic.receiver = mock_receiver
        topic._track_inflight_task(mock_message, mock_task)

        topic._renew_inflight_message_locks()

        mock_receiver.renew_message_lock.assert_called_once_with(mock_message)
        mock_logger.info.assert_called_once_with(
            'Renewed lock for message %s until %s',
            'message-1',
            renewed_until,
        )

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_settle_task_releases_inflight_task(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
    ):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_task = MagicMock()

        mock_message._lock_expired = False
        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_client.get_subscription_receiver.return_value = mock_receiver
        mock_get_context.return_value = MagicMock()

        topic = AzureTopic(config=mock_config, topic_name='mock-topic')
        topic.receiver = mock_receiver
        topic.internal_count = 1
        topic._track_inflight_task(mock_message, mock_task)

        topic._settle_task(
            CompletedTask({'success': True, 'error': None}),
            incoming_message=mock_message,
        )

        self.assertNotIn(topic._get_message_key(mock_message), topic.inflight_tasks)

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_handle_lock_renew_failure_logs_when_sdk_returns_no_error(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_get_context.return_value = MagicMock()
        mock_message.message_id = 'message-1'
        mock_message.locked_until_utc = '2026-03-17T09:39:28Z'
        mock_message.auto_renew_error = None

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)

        topic._handle_lock_renew_failure(mock_message, None)

        mock_logger.error.assert_called_once_with(
            'Error renewing lock for message message-1: lock expired before renewal could complete; '
            'locked_until_utc=2026-03-17T09:39:28Z'
        )


if __name__ == '__main__':
    unittest.main()
