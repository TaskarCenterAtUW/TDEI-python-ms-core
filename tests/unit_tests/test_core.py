import unittest
from unittest.mock import MagicMock, patch, call

from src.python_ms_core import Core
from src.python_ms_core.core.auth.provider.simulated.simulated_authorizer import SimulatedAuthorizer
from src.python_ms_core.core.auth.provider.hosted.hosted_authorizer import HostedAuthorizer

LOCAL_ENV = 'LOCAL'
AZURE_ENV = 'AZURE'
HOSTED_ENV = 'HOSTED'
SIMULATED_ENV = 'SIMULATED'
UNKNOWN_ENV = 'UNKNOWN'


class TestCore(unittest.TestCase):
    def setUp(self):
        self.mock_config = MagicMock()

    def test_get_logger_local_provider(self):
        core = Core(config=LOCAL_ENV)
        with patch('src.python_ms_core.Core.get_logger') as mock_get_logger:
            mock_get_logger.return_value = MagicMock()
            logger = core.get_logger()
            self.assertIsInstance(logger, MagicMock)

    def test_get_logger_azure_provider(self):
        core = Core(config=AZURE_ENV)
        with patch('src.python_ms_core.Core.get_logger') as mock_get_logger:
            mock_get_logger.return_value = MagicMock()
            logger = core.get_logger()
            self.assertIsInstance(logger, MagicMock)

    def test_get_logger_unknown_provider(self):
        core = Core(config=UNKNOWN_ENV)
        with patch('logging.error') as mock_logging_error:
            logger = core.get_logger()
            mock_logging_error.assert_called_once_with(
                f'Failed to initialize core.get_logger for provider: {UNKNOWN_ENV}')

    def test_get_topic_local_provider(self):
        core = Core(config=LOCAL_ENV)
        with patch('src.python_ms_core.Core.get_topic') as mock_get_topic:
            mock_get_topic.return_value = MagicMock()
            topic = core.get_topic('mock_topic')
            self.assertIsInstance(topic, MagicMock)

    def test_get_topic_azure_provider(self):
        self.mock_config.topic.return_value.provider = AZURE_ENV
        core = Core(config=AZURE_ENV)
        with patch('src.python_ms_core.Core.get_topic') as mock_get_topic:
            mock_get_topic.return_value = MagicMock()
            topic = core.get_topic('mock_topic')
            self.assertIsInstance(topic, MagicMock)

    def test_get_topic_unknown_provider(self):
        core = Core(config=UNKNOWN_ENV)
        with patch('logging.error') as mock_logging_error:
            topic = core.get_topic('mock_topic')
            mock_logging_error.assert_called_once_with(
                f'Failed to initialize core.get_topic for provider: {UNKNOWN_ENV}')

    def test_get_storage_client_local_provider(self):
        core = Core(config=LOCAL_ENV)
        with patch('src.python_ms_core.Core.get_storage_client') as mock_get_storage_client:
            mock_get_storage_client.return_value = MagicMock()
            storage_client = core.get_storage_client()
            self.assertIsInstance(storage_client, MagicMock)

    def test_get_storage_client_azure_provider(self):
        core = Core(config=AZURE_ENV)
        with patch('src.python_ms_core.Core.get_storage_client') as mock_get_storage_client:
            mock_get_storage_client.return_value = MagicMock()
            storage_client = core.get_storage_client()
            self.assertIsInstance(storage_client, MagicMock)

    def test_get_storage_client_unknown_provider(self):
        core = Core(config=UNKNOWN_ENV)
        with patch('logging.error') as mock_logging_error:
            storage_client = core.get_storage_client()
            mock_logging_error.assert_called_once_with(
                f'Failed to initialize core.get_storage_client for provider: {UNKNOWN_ENV}')

    def test_get_authorizer_no_config(self):
        core = Core(config=SIMULATED_ENV)
        authorizer = core.get_authorizer()
        self.assertIsInstance(authorizer, SimulatedAuthorizer)

    def test_get_authorizer_with_config_simulated_provider(self):
        config = {'provider': SIMULATED_ENV, 'api_url': 'mock_api_url'}
        core = Core(config=SIMULATED_ENV)
        authorizer = core.get_authorizer(config=config)
        self.assertIsInstance(authorizer, SimulatedAuthorizer)

    def test_get_authorizer_with_config_hosted_provider(self):
        config = {'provider': HOSTED_ENV, 'api_url': 'mock_api_url'}
        core = Core(config=AZURE_ENV)
        authorizer = core.get_authorizer(config=config)
        self.assertIsInstance(authorizer, HostedAuthorizer)

    def test_get_authorizer_with_config_unknown_provider(self):
        config = {'provider': 'UNKNOWN', 'api_url': 'mock_api_url'}
        core = Core(config=UNKNOWN_ENV)
        with patch('logging.error') as mock_logging_error:
            authorizer = core.get_authorizer(config=config)
            mock_logging_error.assert_called_once_with(
                f'Failed to initialize core.get_authorizer for provider: {UNKNOWN_ENV}')


if __name__ == '__main__':
    unittest.main()
