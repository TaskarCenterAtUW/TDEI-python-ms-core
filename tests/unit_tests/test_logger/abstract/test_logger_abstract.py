import unittest
from abc import ABC
from unittest.mock import Mock, MagicMock
from src.python_ms_core.core.logger.abstracts.logger_abstract import LoggerAbstract


class TestLoggerAbstract(unittest.TestCase):

    def setUp(self):
        # Mock the LoggerAbstract since it is an abstract class and cannot be instantiated
        self.logger_mock = MagicMock(spec=LoggerAbstract)

    def test_add_request(self):
        # Simulate a request_data input
        request_data = {"request_id": "12345", "status": "success"}

        # Call the method
        self.logger_mock.add_request(request_data)

        # Assert that add_request was called with the expected request_data
        self.logger_mock.add_request.assert_called_once_with(request_data)

    def test_info(self):
        # Simulate the info message input
        message = "This is an info message"

        # Call the method
        self.logger_mock.info(message)

        # Assert that info method was called with the expected message
        self.logger_mock.info.assert_called_once_with(message)

    def test_debug(self):
        # Simulate the debug message input
        message = "This is a debug message"

        # Call the method
        self.logger_mock.debug(message)

        # Assert that debug method was called with the expected message
        self.logger_mock.debug.assert_called_once_with(message)

    def test_warn(self):
        # Simulate the warn message input
        message = "This is a warning message"

        # Call the method
        self.logger_mock.warn(message)

        # Assert that warn method was called with the expected message
        self.logger_mock.warn.assert_called_once_with(message)

    def test_error(self):
        # Simulate the error message input
        message = "This is an error message"

        # Call the method
        self.logger_mock.error(message)

        # Assert that error method was called with the expected message
        self.logger_mock.error.assert_called_once_with(message)

    def test_record_metric(self):
        # Simulate the metric name and value
        name = "response_time"
        value = "200ms"

        # Call the method
        self.logger_mock.record_metric(name, value)

        # Assert that record_metric method was called with the expected name and value
        self.logger_mock.record_metric.assert_called_once_with(name, value)


if __name__ == '__main__':
    unittest.main()
