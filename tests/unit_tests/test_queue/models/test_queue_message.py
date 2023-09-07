import unittest
import json
from datetime import datetime
from typing import List, Union
from dataclasses import dataclass
from unittest.mock import patch, Mock
from src.python_ms_core.core.queue.models.queue_message import QueueMessage
from src.python_ms_core.core.resource_errors import UnProcessableError


class QueueMessageTestCase(unittest.TestCase):

    def setUp(self):
        self.queue_message = QueueMessage()
        self.queue_message.empty()

    def test_add_message_to_queue(self):
        data = {'key': 'value'}
        self.assertTrue(self.queue_message.add(data))
        self.assertEqual(self.queue_message.get_items(), [data])

    def test_add_message_to_queue_no_data(self):
        self.assertFalse(self.queue_message.add())
        self.assertEqual(self.queue_message.get_items(), [])

    def test_remove_message_from_queue(self):
        data = {'key': 'value'}
        self.queue_message.add(data)
        self.assertTrue(self.queue_message.remove())
        self.assertEqual(self.queue_message.get_items(), [])

    def test_remove_message_from_empty_queue(self):
        self.assertTrue(self.queue_message.remove())

    def test_send_queue(self):
        data = {'key': 'value'}
        self.queue_message.add(data)
        self.assertTrue(self.queue_message.send())
        self.assertEqual(self.queue_message.get_items(), [])

    def test_get_items(self):
        data = {'key': 'value'}
        self.queue_message.add(data)
        items = self.queue_message.get_items()
        self.assertIsInstance(items, List)
        self.assertEqual(items, [data])

    def test_data_from_valid_string(self):
        data = {
            'message': 'some message',
            'data': {'key': 'value'}
        }
        queue_message = QueueMessage.data_from(data)
        self.assertEqual(queue_message.message, 'some message')
        self.assertEqual(queue_message.data, {'key': 'value'})

    def test_data_from_invalid_string(self):
        invalid_data = 'invalid_data'
        with self.assertRaises(UnProcessableError):
            QueueMessage.data_from(invalid_data)

    def test_to_dict(self):
        data = {'key': 'value'}
        self.queue_message.add(data)
        result = self.queue_message.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result, self.queue_message.__dict__)

    def test_validate_string(self):
        value = 'test'
        field = Mock(name='field')  # Create a mock object for the field argument
        result = self.queue_message.validate_string(value, field=field)
        self.assertEqual(result, value)

    def test_validate_string_invalid_type(self):
        value = 123
        field = Mock(name='field')  # Create a mock object for the field argument
        field.name = 'test_field'  # Set the name attribute of the mock field
        with self.assertRaises(ValueError):
            self.queue_message.validate_string(value, field=field)

    def test_validate_data(self):
        value = {'key': 'value'}
        field = Mock(name='field')  # Create a mock object for the field argument
        field.name = 'test_field'  # Set the name attribute of the mock field
        result = self.queue_message.validate_data(value, field=field)
        self.assertEqual(result, value)

    def test_validate_data_invalid_type(self):
        value = 123
        field = Mock(name='field')  # Create a mock object for the field argument
        field.name = 'test_field'  # Set the name attribute of the mock field
        with self.assertRaises(ValueError):
            self.queue_message.validate_data(value, field=field)


if __name__ == '__main__':
    unittest.main()
