import unittest
import concurrent.futures as cf
from unittest.mock import MagicMock, patch

from src.python_ms_core.core.topic.azure_topic import AzureTopic
from src.python_ms_core.core.queue.models.queue_message import QueueMessage


class TestAzureTopic(unittest.TestCase):

    @patch('src.python_ms_core.core.topic.azure_topic.AutoLockRenewer')
    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient')
    def test_subscribe_settles_completed_tasks_on_receiver_loop(self, mock_service_bus_client, mock_auto_lock_renewer):
        mock_client = MagicMock()
        mock_receiver = MagicMock()
        mock_message = MagicMock()
        mock_future = MagicMock()
        mock_config = MagicMock(connection_string='Endpoint=sb://test/')

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


if __name__ == '__main__':
    unittest.main()
