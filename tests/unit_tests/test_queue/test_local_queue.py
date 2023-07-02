import unittest
from unittest.mock import patch, MagicMock
import json
import requests
from src.python_ms_core.core.queue.local_queue import LocalQueue
from src.python_ms_core.core.queue.models.queue_message import QueueMessage


class TestLocalQueue(unittest.TestCase):
    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.queue_name = 'MockQueue'
        self.mock_config.provider = 'MockLocal'

    def test_send_with_data(self):
        data = {'key': 'value'}
        message_dict = QueueMessage.to_dict(data)
        url = f'{self.mock_config.queue_name}/log'

        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200

            queue = LocalQueue(self.mock_config)
            queue.send(data)

            mock_post.assert_called_once_with(url, json=message_dict)
            self.assertEqual(queue.get_items(), [])

    def test_send_without_data(self):
        with patch('requests.post') as mock_post:
            queue = LocalQueue(self.mock_config)
            queue.send()

            mock_post.assert_not_called()
            self.assertEqual(queue.get_items(), [])

    def test_add_message_to_queue(self):
        data = {'key': 'value'}
        message_str = json.dumps(data)
        queue = LocalQueue(self.mock_config)
        queue.empty()
        queue.add(data)

        self.assertEqual(queue.get_items(), [message_str])

    def test_add_message_to_queue_with_no_data(self):
        queue = LocalQueue(self.mock_config)
        queue.empty()
        self.assertEqual(queue.get_items(), [])

    def test_remove_message_from_queue(self):
        data = {'key': 'value'}
        queue = LocalQueue(self.mock_config)
        queue.empty()
        queue.add(data)
        queue.remove()

        self.assertEqual(queue.get_items(), [])

    def test_get_items_from_queue(self):
        data1 = {'key': 'value1'}
        data2 = {'key': 'value2'}
        message_str1 = json.dumps(data1)
        message_str2 = json.dumps(data2)

        queue = LocalQueue(self.mock_config)
        queue.empty()
        queue.add(data1)
        queue.add(data2)

        self.assertEqual(queue.get_items(), [message_str2, message_str1])

    def test_empty_queue(self):
        data = {'key': 'value1'}
        queue = LocalQueue(self.mock_config)
        queue.add(data)
        queue.empty()

        self.assertEqual(queue.get_items(), [])


if __name__ == '__main__':
    unittest.main()
