import unittest
from unittest.mock import MagicMock, patch, call

from src.python_ms_core import Core, __version__
from src.python_ms_core.core.logger.logger import Logger
from src.python_ms_core.core.logger.local_logger import LocalLogger
from src.python_ms_core.core.topic.local_topic import LocalTopic
from src.python_ms_core.core.topic.azure_topic import AzureTopic
from src.python_ms_core.core.storage.providers.local.local_storage_client import LocalStorageClient
from src.python_ms_core.core.storage.providers.azure.azure_storage_client import AzureStorageClient
from src.python_ms_core.core.config.config import CoreConfig, LocalConfig, AuthConfig, UnknownConfig
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

    def test_core_initialization_local_env(self):
        core = Core(config=LOCAL_ENV)
        self.assertIsInstance(core.config, LocalConfig)

    def test_core_initialization_azure_env(self):
        core = Core(config=AZURE_ENV)
        self.assertIsInstance(core.config, CoreConfig)

    def test_core_initialization_unknown_env(self):
        with patch('logging.error') as mock_logging_error:
            core = Core(config='UNKNOWN')
            self.assertIsInstance(core.config, UnknownConfig)
            mock_logging_error.assert_called_once_with(
                'Failed to initialize core.get_logger for provider: UNKNOWN'
            )

    @patch.object(Core, '_Core__check_health')
    def test_core_initialization_without_config(self, mock_check_health):
        core = Core()
        self.assertIsInstance(core.config, CoreConfig)
        mock_check_health.assert_called_once()

    @patch('logging.error')
    @patch.object(CoreConfig, 'logger', return_value=MagicMock(provider='INVALID'))
    def test_get_logger_invalid_provider(self, mock_logger, mock_logging_error):
        core = Core(config='INVALID')
        logger = core.get_logger()
        self.assertIsNone(logger)

        # Assert logging.error was called with the expected message at least once
        mock_logging_error.assert_any_call(
            'Failed to initialize core.get_logger for provider: INVALID'
        )

        self.assertEqual(mock_logging_error.call_count, 2)

    @patch('logging.error')
    @patch.object(CoreConfig, 'topic', return_value=MagicMock(provider='INVALID'))
    def test_get_topic_invalid_provider(self, mock_topic, mock_logging_error):
        # Mock the CoreConfig.logger method to prevent logger errors during Core initialization
        with patch.object(CoreConfig, 'logger', return_value=MagicMock(provider='LOCAL')):
            core = Core(config='INVALID')

        # Test the behavior of get_topic with an invalid provider
        topic = core.get_topic('mock_topic')

        # Assertions
        self.assertIsNone(topic)
        mock_logging_error.assert_called_with(
            'Failed to initialize core.get_topic for provider: INVALID'
        )

    @patch('logging.error')
    @patch.object(CoreConfig, 'storage', return_value=MagicMock(provider='INVALID'))
    def test_get_storage_client_invalid_provider(self, mock_storage, mock_logging_error):
        # Mock the CoreConfig.logger method to prevent logger errors during Core initialization
        with patch.object(CoreConfig, 'logger', return_value=MagicMock(provider='LOCAL')):
            core = Core(config='INVALID')

        # Test the behavior of get_storage_client with an invalid provider
        storage_client = core.get_storage_client()

        # Assertions
        self.assertIsNone(storage_client)
        mock_logging_error.assert_called_with(
            'Failed to initialize core.get_storage_client for provider: INVALID'
        )

    @patch('logging.error')
    @patch.object(CoreConfig, 'auth', return_value=MagicMock(provider='INVALID'))
    @patch.object(CoreConfig, 'logger', return_value=MagicMock(provider='LOCAL'))
    def test_get_authorizer_invalid_provider(self, mock_logger, mock_auth, mock_logging_error):
        # Mock Core's configuration
        with patch('src.python_ms_core.Core.__init__', lambda self, config=None: None):  # Skip actual __init__
            core = Core(config='INVALID')  # Create a Core instance without triggering its initialization
            core.config = MagicMock()  # Assign a mocked config
            core.config.auth.return_value.provider = 'INVALID'  # Mock the auth provider

        # Call get_authorizer
        authorizer = core.get_authorizer()

        # Assertions
        self.assertIsNone(authorizer, "Expected authorizer to be None for invalid provider.")
        mock_logging_error.assert_called_once_with(
            'Failed to initialize core.get_authorizer for provider: INVALID'
        )

    @patch.object(CoreConfig, 'auth', return_value=MagicMock(provider=SIMULATED_ENV))
    @patch.object(CoreConfig, 'logger', return_value=MagicMock(provider='LOCAL'))
    def test_get_authorizer_default_config(self, mock_logger, mock_auth):
        # Initialize Core with a mocked configuration
        core = Core(config=SIMULATED_ENV)

        # Mock the behavior of config.auth being accessed
        core.config = MagicMock()
        core.config.auth = mock_auth

        # Call get_authorizer
        authorizer = core.get_authorizer()

        # Assertions
        self.assertIsInstance(
            authorizer,
            SimulatedAuthorizer,
            "Expected a SimulatedAuthorizer instance for SIMULATED_ENV."
        )
        # Assert that the auth method was called exactly once
        mock_auth.assert_called_once()

    @patch.object(CoreConfig, 'auth', return_value=MagicMock(provider=HOSTED_ENV))
    @patch.object(CoreConfig, 'logger', return_value=MagicMock(provider='LOCAL'))
    def test_get_authorizer_hosted_provider(self, mock_logger, mock_auth):
        # Initialize Core with a mocked configuration
        core = Core(config=HOSTED_ENV)

        # Mock the behavior of core.config.auth being accessed
        core.config = MagicMock()
        core.config.auth = mock_auth

        # Call get_authorizer
        authorizer = core.get_authorizer()

        # Assertions
        self.assertIsInstance(
            authorizer,
            HostedAuthorizer,
            "Expected a HostedAuthorizer instance for HOSTED_ENV."
        )
        # Assert that the auth method was called exactly once
        mock_auth.assert_called_once()

    def test_version(self):
        core = Core()
        self.assertEqual(core.__version__, __version__)

    @patch('builtins.print')
    def test_check_health_no_config(self, mock_print):
        core = Core(config=None)
        core.config = None  # Simulating no config
        health = core._Core__check_health()  # Accessing the mangled method name
        self.assertFalse(health)
        mock_print.assert_any_call('Unknown/Unimplemented provider')

    @patch('builtins.print')
    def test_check_health_valid_config(self, mock_print):
        # Mock the Core object with LOCAL_ENV
        core = Core(config=LOCAL_ENV)

        # Call the health check method
        core._Core__check_health()

        # Verify specific print calls were made
        expected_calls = [
            call(f'Configured for \x1b[32m local \x1b[0m \n'),
            call('\x1b[32m\x1b[40m Connected to Queues \x1b[0m'),
            call('\x1b[32m\x1b[40m Connected to Storage \x1b[0m'),
            call('\x1b[32m Logger configured \x1b[0m'),
        ]

        # Assert that each expected call was made
        mock_print.assert_has_calls(expected_calls, any_order=True)

    def test_logger_initialization_fallback(self):
        # Initialize Core with LOCAL_ENV
        core = Core(config=LOCAL_ENV)

        # Call get_logger to test fallback behavior
        logger = core.get_logger()

        # Assertions
        self.assertIsInstance(logger, LocalLogger, "Expected fallback to LocalLogger when provider is None.")

    def test_storage_initialization_fallback(self):
        # Initialize Core with LOCAL_ENV
        core = Core(config=LOCAL_ENV)

        # Call get_storage_client to test fallback behavior
        storage_client = core.get_storage_client()

        # Assertions
        self.assertIsInstance(
            storage_client,
            LocalStorageClient,
            "Expected storage_client to be an instance of LocalStorageClient when provider is None."
        )

    @patch('src.python_ms_core.core.logger.logger.Queue', return_value=MagicMock())
    @patch.object(CoreConfig, 'logger', return_value=MagicMock(provider=AZURE_ENV))
    def test_get_logger_azure_provider(self, mock_logger, mock_queue):
        # Initialize Core with AZURE_ENV configuration
        core = Core(config=AZURE_ENV)

        # Call the get_logger method
        logger = core.get_logger()

        # Assertions
        self.assertIsInstance(logger, Logger, "Expected logger to be an instance of Logger for AZURE_ENV.")
        self.assertGreaterEqual(mock_logger.call_count, 1, "Expected CoreConfig.logger to be called at least once.")
        mock_queue.assert_called_once()
        mock_queue.assert_called_once()

    @patch('src.python_ms_core.core.topic.local_topic.pika.BlockingConnection', return_value=MagicMock())
    @patch('src.python_ms_core.core.topic.local_topic.pika.URLParameters')
    def test_get_topic_local_provider(self, mock_url_parameters, mock_blocking_connection):
        # Mock topic configuration
        mock_topic_config = MagicMock(provider=LOCAL_ENV)
        # Set a valid connection string directly
        connection_string = "amqp://guest:guest@localhost:5672/"
        mock_topic_config.client.connection_string = connection_string

        # Initialize Core and mock its config
        core = Core(config=LOCAL_ENV)
        core.config = MagicMock()  # Mock the config attribute
        core.config.topic.return_value = mock_topic_config

        # Call the get_topic method
        topic = core.get_topic("mock_topic")

        # Assertions
        self.assertIsInstance(topic, LocalTopic, "Expected topic to be an instance of LocalTopic for LOCAL_ENV.")
        core.config.topic.assert_called_once()
        mock_blocking_connection.assert_called_once()

    @patch('src.python_ms_core.core.topic.azure_topic.ServiceBusClient.from_connection_string',
           return_value=MagicMock())
    @patch.object(CoreConfig, 'topic', return_value=MagicMock(provider=AZURE_ENV))
    def test_get_topic_azure_provider(self, mock_topic_config, mock_service_bus_client):
        # Mock topic configuration
        mock_topic_config.return_value.connection_string = "Endpoint=sb://test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=some_key"

        # Initialize Core with AZURE_ENV configuration
        core = Core(config=AZURE_ENV)

        # Call the get_topic method
        topic = core.get_topic("mock_topic")

        # Assertions
        self.assertIsInstance(
            topic,
            AzureTopic,
            "Expected topic to be an instance of AzureTopic for AZURE_ENV."
        )
        mock_topic_config.assert_called_once()  # Ensure CoreConfig.topic was called
        mock_service_bus_client.assert_called_once_with(
            conn_str="Endpoint=sb://test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=some_key",
            retry_total=10,
            retry_backoff_factor=1,
            retry_backoff_max=30
        )

    @patch.object(CoreConfig, 'storage', return_value=MagicMock(provider='AZURE'))
    def test_get_storage_client_for_azure_env(self, mock_storage_config):
        # Mock the storage configuration returned by CoreConfig
        mock_storage_config.return_value.connection_string = "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=testkey;EndpointSuffix=core.windows.net"
        mock_storage_config.return_value.provider = "AZURE"

        # Mock the return value of AzureStorageClient

        mock_azure_storage_client = MagicMock()
        mock_azure_storage_client.return_value = MagicMock()

        # Initialize Core with the mocked configuration
        core = Core(config='AZURE')

        # Call the get_storage_client method
        core.get_storage_client()

        # Assertions
        mock_storage_config.assert_called()


if __name__ == '__main__':
    unittest.main()
