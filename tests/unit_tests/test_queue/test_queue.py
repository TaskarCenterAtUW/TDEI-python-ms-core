import unittest
from unittest.mock import patch, MagicMock
import json
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from src.python_ms_core.core.queue.queue import Queue
from src.python_ms_core.core.queue.models.queue_message import QueueMessage
from src.python_ms_core.core.queue.config.queue_config import Config


class TestQueue(unittest.TestCase):

    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.queue_name = 'mock_queue_name'
        self.mock_config.provider = 'Azure'
        self.mock_config.provider = 'Azure'

    def test_send_with_data(self):
        # Mock the ServiceBusClient.from_connection_string method
        with patch.object(ServiceBusClient, 'from_connection_string') as mock_from_connection_string:
            # Create a Config instance with the mock config
            self.mock_config.connection_string = mock_from_connection_string
            queue = Queue(self.mock_config)
            data = {'key': 'value'}
            queue.send(data)
            # Additional assertions
            mock_from_connection_string.assert_called_once_with(
                conn_str=self.mock_config.connection_string, logging_enable=False, retry_total=0
            )
            self.assertEqual(queue.queue, [])

    def test_send_no_data(self):
        # Mock the ServiceBusClient.from_connection_string method
        with patch.object(ServiceBusClient, 'from_connection_string') as mock_from_connection_string:
            # Create a Config instance with the mock config
            self.mock_config.connection_string = mock_from_connection_string
            queue = Queue(self.mock_config)
            queue.send()
            # Additional assertions
            mock_from_connection_string.assert_called_once_with(
                conn_str=self.mock_config.connection_string, logging_enable=False, retry_total=0
            )

            self.assertEqual(queue.queue, [])

    def test_add(self):
        # Mock the ServiceBusClient.from_connection_string method
        with patch.object(ServiceBusClient, 'from_connection_string'):
            data = {'key': 'value'}
            queue = Queue(self.mock_config)
            queue.empty()
            queue.add(data)

            self.assertEqual(queue.get_items(), [json.dumps(data)])

    def test_add_no_data(self):
        # Mock the ServiceBusClient.from_connection_string method
        with patch.object(ServiceBusClient, 'from_connection_string'):
            queue = Queue(self.mock_config)
            queue.empty()
            queue.add(None)

            self.assertEqual(queue.get_items(), [])

    def test_remove(self):
        # Mock the ServiceBusClient.from_connection_string method
        with patch.object(ServiceBusClient, 'from_connection_string'):
            queue = Queue(self.mock_config)
            queue.empty()
            data1 = {'key': 'value1'}
            data2 = {'key': 'value2'}
            queue.add(data1)
            queue.add(data2)

            queue.remove()
            self.assertEqual(queue.get_items(), [json.dumps(data2)])

            queue.remove()
            self.assertEqual(queue.get_items(), [])

    def test_get_items(self):
        with patch.object(ServiceBusClient, 'from_connection_string'):
            data = {'key': 'value'}
            queue = Queue(self.mock_config)
            queue.empty()
            queue.add(data)
            items = queue.get_items()
            self.assertEqual(items, [json.dumps(data)])
            self.assertEqual(queue.get_items(), [json.dumps(data)])

    def test_empty(self):
        with patch.object(ServiceBusClient, 'from_connection_string'):
            data = {'key': 'value'}

            queue = Queue(self.mock_config)
            queue.add(data)

            queue.empty()
            self.assertEqual(queue.get_items(), [])


if __name__ == '__main__':
    unittest.main()
