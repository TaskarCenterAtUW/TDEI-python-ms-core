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
        mock_thread = MagicMock()

        with patch('threading.Thread', return_value=mock_thread) as mock_thread_class:
            topic = Topic(config=self.mock_config, topic_name='mock_topic')
            topic.provider = mock_provider
            mock_provider.client = mock_client

            with patch.object(Callback, 'start_listening', return_value=None) as mock_start_listening:
                topic.subscribe(subscription='mock_subscription', callback=mock_callback)

                # Assertions on the objects
                mock_thread.start.assert_called_once()
                mock_thread_class.assert_called_once_with(
                    target=mock_start_listening,
                    args=(mock_provider, 'mock_topic', 'mock_subscription')
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


if __name__ == '__main__':
    unittest.main()
