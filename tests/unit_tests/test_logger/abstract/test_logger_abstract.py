import unittest
from unittest.mock import Mock
from src.python_ms_core.core.logger.abstracts.logger_abstract import LoggerAbstract


class MockLogger(LoggerAbstract):
    def __init__(self, config=None):
        super().__init__(config)

    def add_request(self, request_data):
        pass

    def info(self, message: str):
        pass

    def debug(self, message: str):
        pass

    def warn(self, message: str):
        pass

    def error(self, message: str):
        pass


class TestLoggerAbstract(unittest.TestCase):
    def test_add_request(self):
        logger = MockLogger()
        logger.add_request = Mock()

        request_data = {'key': 'value'}
        logger.add_request(request_data)

        logger.add_request.assert_called_once_with(request_data)

    def test_info(self):
        logger = MockLogger()
        logger.info = Mock()

        message = 'This is an info message.'
        logger.info(message)

        logger.info.assert_called_once_with(message)

    def test_debug(self):
        logger = MockLogger()
        logger.debug = Mock()

        message = 'This is a debug message.'
        logger.debug(message)

        logger.debug.assert_called_once_with(message)

    def test_warn(self):
        logger = MockLogger()
        logger.warn = Mock()

        message = 'This is a warning message.'
        logger.warn(message)

        logger.warn.assert_called_once_with(message)

    def test_error(self):
        logger = MockLogger()
        logger.error = Mock()

        message = 'This is an error message.'
        logger.error(message)

        logger.error.assert_called_once_with(message)

    def test_record_metric(self):
        logger = MockLogger()
        logger.record_metric = Mock()

        name = 'metric_name'
        value = 'metric_value'
        logger.record_metric(name, value)

        logger.record_metric.assert_called_once_with(name, value)


if __name__ == '__main__':
    unittest.main()
