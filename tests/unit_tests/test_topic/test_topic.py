import unittest
import json
import uuid
import random
from unittest.mock import MagicMock, patch
from src.python_ms_core.core.topic.topic import Topic, Callback
from src.python_ms_core.core.queue.models.queue_message import QueueMessage


class TestTopic(unittest.TestCase):

    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.provider = 'mock_provider'
        self.mock_config.connection_string = 'mock_connection_string'
        self.mock_config.topic_name = 'mock_topic_name'

    def test_subscribe_with_subscription(self):
        mock_callback = MagicMock()
        mock_provider = MagicMock()
        mock_client = MagicMock()

        topic = Topic(config=self.mock_config, topic_name='mock_topic')
        topic.provider = mock_provider
        mock_provider.client = mock_client

        with patch.object(Callback, 'start_listening', return_value=None) as mock_start_listening:
            topic.subscribe(subscription='mock_subscription', callback=mock_callback)

            # Assertions on the objects
            mock_start_listening.assert_called_once_with(mock_provider, 'mock_topic', 'mock_subscription')

    def test_subscribe_without_subscription(self):
        mock_callback = MagicMock()
        mock_provider = MagicMock()
        mock_client = MagicMock()

        topic = Topic(config=self.mock_config, topic_name='mock_topic')
        topic.provider = mock_provider
        mock_provider.client = mock_client

        with patch('logging.error') as mock_logging_error:
            topic.subscribe(subscription=None, callback=mock_callback)

            # Assertions
            mock_logging_error.assert_called_once_with(
                f'Unimplemented initialize for core {mock_provider.provider}, Subscription name is required!'
            )

    def test_publish(self):
        data = {'test': random.randint(0, 1000)}
        mock_data = QueueMessage.data_from({
            'message': str(uuid.uuid4().hex),
            'data': data
        })
        mock_provider = MagicMock()
        mock_client = MagicMock()
        mock_sender = MagicMock()

        topic = Topic(config=self.mock_config, topic_name='mock_topic')
        topic.provider = mock_provider
        mock_provider.client = mock_client
        mock_client.get_topic_sender.return_value = mock_sender
        mock_message = QueueMessage.to_dict(mock_data)
        mock_json_message = json.dumps(mock_message)
        mock_sender.send_messages.return_value = mock_json_message

        topic.publish(data=mock_data)

        # Assertions on the objects
        mock_client.get_topic_sender.assert_called_once_with(topic_name=mock_provider.topic)
        mock_sender.send_messages.assert_called_once()


class TestCallback(unittest.TestCase):

    def setUp(self):
        self.mock_function = MagicMock()
        self.callback = Callback(fn=self.mock_function, max_concurrent_messages=2)
        self.mock_message = MagicMock()
        self.mock_receiver = MagicMock()
        self.mock_provider = MagicMock()
        self.mock_topic_receiver = MagicMock()
        self.mock_provider.client.get_subscription_receiver.return_value = self.mock_topic_receiver
        self.mock_topic_receiver.receive_messages.return_value = [self.mock_message]

    def test_renew_message_lock(self):
        self.mock_message._lock_expired = False
        self.callback._renewal_interval = 0  # For fast testing
        with patch.object(self.mock_receiver, 'renew_message_lock') as mock_renew_message_lock:
            with patch('time.sleep', side_effect=[None, Exception()]):
                self.callback._renew_message_lock(self.mock_message, self.mock_receiver)
                mock_renew_message_lock.assert_called_with(self.mock_message)

    @patch('threading.Thread')
    def test_process_message_lock_expired(self, mock_thread_class):
        self.mock_message._lock_expired = True
        with patch.object(QueueMessage, 'data_from', return_value=QueueMessage()):
            self.callback.process_message(self.mock_message, self.mock_receiver)
            self.mock_function.assert_called_once()
            mock_thread_class.assert_not_called()

    @patch('threading.Thread')
    def test_process_message(self, mock_thread_class):
        self.mock_message._lock_expired = False
        with patch.object(QueueMessage, 'data_from', return_value=QueueMessage()):
            self.callback.process_message(self.mock_message, self.mock_receiver)
            self.mock_function.assert_called_once()
            mock_thread_class.assert_called_once()

    def test_process_message_in_thread_success(self):
        with patch.object(self.callback, 'process_message') as mock_process_message:
            self.callback.message_processing = 1
            self.callback._process_message_in_thread(self.mock_message, self.mock_receiver)
            mock_process_message.assert_called_once_with(message=self.mock_message, receiver=self.mock_receiver)
            self.mock_receiver.complete_message.assert_called_once_with(self.mock_message)
            self.assertEqual(self.callback.message_processing, 0)

    def test_process_message_in_thread_process_message_error(self):
        with patch.object(self.callback, 'process_message', side_effect=Exception("Mocked Exception")):
            self.callback.message_processing = 1
            self.callback._process_message_in_thread(self.mock_message, self.mock_receiver)
            self.mock_receiver.complete_message.assert_called_once_with(self.mock_message)
            self.assertEqual(self.callback.message_processing, 0)

    def test_process_message_in_thread_complete_message_error(self):
        with patch.object(self.callback, 'process_message'):
            self.mock_receiver.complete_message.side_effect = Exception("Mocked Exception")
            self.callback.message_processing = 1
            self.callback._process_message_in_thread(self.mock_message, self.mock_receiver)
            self.mock_receiver.complete_message.assert_called_once_with(self.mock_message)
            self.assertEqual(self.callback.message_processing, 0)

    @patch('src.python_ms_core.core.topic.topic.logger')
    def test_process_message_in_thread_both_errors(self, mock_logger):
        with patch.object(self.callback, 'process_message', side_effect=Exception("Mocked Process Exception")):
            self.mock_receiver.complete_message.side_effect = Exception("Mocked Complete Exception")
            self.callback.message_processing = 1
            self.callback._process_message_in_thread(self.mock_message, self.mock_receiver)
            self.mock_receiver.complete_message.assert_called_once_with(self.mock_message)
            self.assertEqual(self.callback.message_processing, 0)
            self.assertEqual(mock_logger.error.call_count, 2)
            mock_logger.error.assert_any_call(
                f'Error: Mocked Process Exception, Invalid message received: {self.mock_message}')
            mock_logger.error.assert_any_call(f'Error completing the message: Mocked Complete Exception')


if __name__ == '__main__':
    unittest.main()
