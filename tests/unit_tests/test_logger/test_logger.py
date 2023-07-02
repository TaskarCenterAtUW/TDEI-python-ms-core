import unittest
from unittest.mock import Mock, patch

from src.python_ms_core.core.logger.logger import Logger
from src.python_ms_core.core.queue.models.queue_message import QueueMessage


class TestLogger(unittest.TestCase):
    @patch('src.python_ms_core.core.queue.queue.Queue')
    def setUp(self, MockQueue):
        self.config = Mock()
        self.queue_client = MockQueue.return_value
        self.logger = Logger(config=self.config)
        self.logger.queue_client = self.queue_client

    def test_add_request(self):
        request_data = {'key': 'value'}
        self.logger.add_request(request_data)

        expected_message = QueueMessage(
            message='Add Request',
            messageType='addRequest',
            data=request_data
        )
        self.queue_client.send.assert_called_once_with(expected_message)

    def test_info(self):
        message = 'This is an info message.'
        self.logger.info(message)

        expected_message = QueueMessage(
            message=message,
            messageType='info'
        )
        self.queue_client.send.assert_called_once_with(expected_message)

    def test_debug(self):
        message = 'This is a debug message.'
        self.logger.debug(message)

        expected_message = QueueMessage(
            message=message,
            messageType='debug'
        )
        self.queue_client.send.assert_called_once_with(expected_message)

    def test_warn(self):
        message = 'This is a warning message.'
        self.logger.warn(message)

        expected_message = QueueMessage(
            message=message,
            messageType='warn'
        )
        self.queue_client.send.assert_called_once_with(expected_message)

    def test_error(self):
        message = 'This is an error message.'
        self.logger.error(message)

        expected_message = QueueMessage(
            message=message,
            messageType='error'
        )
        self.queue_client.send.assert_called_once_with(expected_message)

    def test_record_metric(self):
        name = 'metric_name'
        value = 'metric_value'
        self.logger.record_metric(name, value)

        expected_message = QueueMessage(
            message='metric',
            messageType='metric',
            data={'name': name, 'value': value}
        )
        self.queue_client.send.assert_called_once_with(expected_message)


if __name__ == '__main__':
    unittest.main()
