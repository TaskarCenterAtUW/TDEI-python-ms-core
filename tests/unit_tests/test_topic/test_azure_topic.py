import unittest
import concurrent.futures as cf
from unittest.mock import MagicMock, patch

from src.python_ms_core.core.topic.azure_topic import AzureTopic
from src.python_ms_core.core.queue.models.queue_message import QueueMessage


class TestAzureTopic(unittest.TestCase):

    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_init_sets_long_running_lock_renewal_defaults(self, mock_service_bus_client, mock_auto_lock_renewer):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_renewer = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_auto_lock_renewer.return_value = mock_renewer

        AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)

        mock_auto_lock_renewer.assert_called_once()
        _, kwargs = mock_auto_lock_renewer.call_args
        self.assertEqual(kwargs['max_lock_renewal_duration'], 86400)
        self.assertEqual(kwargs['max_workers'], 2)
        self.assertEqual(mock_renewer._renew_period, 60)

    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_subscribe_settles_completed_tasks_on_receiver_loop(self, mock_service_bus_client, mock_auto_lock_renewer):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_future = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message._lock_expired = False

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_client.get_subscription_receiver.return_value = mock_receiver
        mock_receiver.receive_messages.side_effect = [[mock_message]]

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        callback = MagicMock()
        
        def submit_side_effect(fn, *args, **kwargs):
            mock_future = cf.Future()
            mock_future.set_result(fn(*args, **kwargs))
            return mock_future

        topic.executor.submit = MagicMock(side_effect=submit_side_effect)
        with patch.object(QueueMessage, 'data_from', return_value=QueueMessage()):
            topic.subscribe(subscription='mock-subscription', callback=callback, max_receivable_messages=1)

        callback.assert_called_once()
        mock_auto_lock_renewer.return_value.register.assert_called_once()
        mock_receiver.complete_message.assert_called_once_with(mock_message)
        mock_receiver.abandon_message.assert_not_called()

    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_settle_task_logs_error_and_releases_slot(self, mock_service_bus_client, mock_auto_lock_renewer, mock_logger):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_future = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message._lock_expired = False

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_client.get_subscription_receiver.return_value = mock_receiver
        mock_future.result.return_value = [True, mock_message]
        mock_receiver.complete_message.side_effect = Exception('Mocked settlement failure')

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic.receiver = mock_receiver
        topic.internal_count = 1

        topic._settle_task(mock_future, incoming_message=mock_message)

        mock_receiver.complete_message.assert_called_once_with(mock_message)
        mock_logger.error.assert_called_once_with('Error in settling message: Mocked settlement failure')
        self.assertEqual(topic.internal_count, 0)

    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_settle_task_skips_expired_message(self, mock_service_bus_client, mock_auto_lock_renewer, mock_logger):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_future = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')

        mock_message._lock_expired = True
        mock_message.message_id = 'message-1'
        mock_message.locked_until_utc = '2026-03-17T09:39:28Z'
        mock_message.auto_renew_error = None
        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_client.get_subscription_receiver.return_value = mock_receiver
        mock_future.result.return_value = [True, mock_message]

        topic = AzureTopic(config=mock_config, topic_name='mock-topic', max_concurrent_messages=1)
        topic.receiver = mock_receiver
        topic.internal_count = 1

        topic._settle_task(mock_future, incoming_message=mock_message)

        mock_receiver.complete_message.assert_not_called()
        mock_receiver.abandon_message.assert_not_called()
        mock_logger.error.assert_called_once_with(
            'Skipping settlement for message message-1 because the lock expired at '
            '2026-03-17T09:39:28Z. auto_renew_error=None'
        )
        self.assertEqual(topic.internal_count, 0)

    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_handle_lock_renew_failure_logs_when_sdk_returns_no_error(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_message = MagicMock()

        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
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

    @patch('src.python_ms_core.core.topic.azure_topic.logger')
    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_lock_renew_attempt_logs_memory_snapshot(
        self,
        mock_service_bus_client,
        mock_auto_lock_renewer,
        mock_logger,
    ):
        mock_client = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')
        mock_service_bus_client.from_connection_string.return_value = mock_client
        mock_client.get_topic_sender.return_value = MagicMock()
        mock_auto_lock_renewer.return_value = MagicMock()

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
