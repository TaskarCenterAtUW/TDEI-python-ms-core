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

    @patch.dict(os.environ, {}, clear=True)
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
            topic.lock_renew_receiver,
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
        topic._get_runtime_snapshot = MagicMock(
            return_value=(
                'memory=rss_mb=128.00, vms_mb=256.00, num_threads=4, '
                'cpu=process_percent=80.00, system_percent=91.00, '
                'gc=enabled=True, counts=(1, 2, 3), thresholds=(700, 10, 10), '
                'stats=gen0[collections=1, collected=2, uncollectable=0]'
            )
        )

        topic._handle_lock_renew_failure(mock_message, None)

        mock_logger.error.assert_called_once_with(
            'Error renewing lock for message message-1: lock expired before renewal could complete; '
            'locked_until_utc=2026-03-17T09:39:28Z; '
            'runtime_snapshot=memory=rss_mb=128.00, vms_mb=256.00, num_threads=4, '
            'cpu=process_percent=80.00, system_percent=91.00, '
            'gc=enabled=True, counts=(1, 2, 3), thresholds=(700, 10, 10), '
            'stats=gen0[collections=1, collected=2, uncollectable=0]'
        )

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_context')
    @patch('src.python_ms_core.core.topic.azure_topic.mp.get_all_start_methods', return_value=['fork', 'spawn'])
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_lock_renew_attempt_logs_memory_snapshot(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_get_all_start_methods,
        mock_get_context,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_auto_lock_renewer.return_value = MagicMock()
        mock_get_context.return_value = MagicMock()

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic._get_runtime_snapshot = MagicMock(
            return_value=(
                'memory=rss_mb=64.00, vms_mb=128.00, num_threads=3, '
                'cpu=process_percent=55.00, system_percent=70.00, '
                'gc=enabled=True, counts=(4, 5, 6), thresholds=(700, 10, 10), '
                'stats=gen0[collections=3, collected=10, uncollectable=0]'
            )
        )

        mock_message = MagicMock()
        mock_message.message_id = 'message-2'
        mock_message.locked_until_utc = '2026-03-17T09:39:33Z'
        topic.receiver = MagicMock()

        topic.lock_renew_receiver.renew_message_lock(mock_message)

        mock_logger.info.assert_any_call(
            'Attempting lock renewal for message %s; locked_until_utc=%s; runtime_snapshot=%s',
            'message-2',
            '2026-03-17T09:39:33Z',
            'memory=rss_mb=64.00, vms_mb=128.00, num_threads=3, '
            'cpu=process_percent=55.00, system_percent=70.00, '
            'gc=enabled=True, counts=(4, 5, 6), thresholds=(700, 10, 10), '
            'stats=gen0[collections=3, collected=10, uncollectable=0]',
        )
        topic.receiver.renew_message_lock.assert_called_once_with(mock_message)


if __name__ == '__main__':
    unittest.main()
