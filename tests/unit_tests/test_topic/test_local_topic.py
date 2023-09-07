import unittest
from unittest.mock import MagicMock, patch
import pika
from src.python_ms_core.core.topic.local_topic import LocalTopic
from src.python_ms_core.core.topic.config.topic_config import Config


class TestLocalTopic(unittest.TestCase):

    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.provider = 'mock_provider'
        self.mock_config.connection_string = 'amqp://guest:guest@localhost:1567/'
        self.mock_config.topic_name = 'mock_topic_name'

    def test_subscribe_with_subscription(self):
        mock_callback = MagicMock()
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_client = MagicMock(spec=Config)

        with patch('pika.BlockingConnection') as mock_blocking_connection:
            mock_blocking_connection.return_value = mock_connection
            mock_connection.channel.return_value = mock_channel
            local_topic = LocalTopic(config=self.mock_config, topic_name='mock_topic')

            with patch.object(local_topic, 'client', mock_client):
                local_topic.subscribe(subscription='mock_subscription', callback=mock_callback)

                # Assertions on the objects
                self.assertEqual(local_topic.connection, mock_connection)
                self.assertEqual(local_topic.channel, mock_channel)

    def test_publish(self):
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_client = MagicMock()

        with patch('pika.BlockingConnection') as mock_blocking_connection:
            mock_blocking_connection.return_value = mock_connection
            mock_connection.channel.return_value = mock_channel
            local_topic = LocalTopic(config=self.mock_config, topic_name='mock_topic')

            with patch.object(local_topic, 'client', mock_client):
                mock_data = MagicMock()
                local_topic.publish(data=mock_data)

                # Assertions on the objects
                self.assertEqual(local_topic.client, mock_client)
                self.assertEqual(local_topic.connection, mock_connection)
                self.assertEqual(local_topic.channel, mock_channel)


if __name__ == '__main__':
    unittest.main()
