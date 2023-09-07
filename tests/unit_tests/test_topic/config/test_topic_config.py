import unittest
from unittest.mock import MagicMock, patch
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from src.python_ms_core.core.topic.config.topic_config import Config
import logging


class TestConfig(unittest.TestCase):
    def test_non_azure_provider(self):
        # Create a mock config object
        mock_config = MagicMock()
        mock_config.provider = 'NonAzure'

        # Create a Config instance with the mock config
        config = Config(config=mock_config)

        # Perform assertions
        self.assertEqual(config.provider, 'NonAzure')
        self.assertFalse(hasattr(config, 'client'))  # Check if 'client' attribute is absent
        self.assertFalse(hasattr(config, 'sender'))  # Check if 'sender' attribute is absent

    def test_azure_provider_valid_connection_string(self):
        # Create a mock config object
        mock_config = MagicMock()
        mock_config.provider = 'Azure'
        mock_config.connection_string = 'valid_connection_string'
        mock_config.topic_name = 'mock_topic_name'

        # Mock the ServiceBusClient.from_connection_string method
        with patch.object(ServiceBusClient, 'from_connection_string') as mock_from_connection_string:
            # Create a Config instance with the mock config
            config = Config(config=mock_config)

            # Perform assertions
            self.assertEqual(config.provider, 'Azure')
            self.assertEqual(config.connection_string, 'valid_connection_string')
            mock_from_connection_string.assert_called_once_with(
                conn_str='valid_connection_string',
                retry_total=10,
                retry_backoff_factor=1,
                retry_backoff_max=30
            )

    def test_azure_provider_invalid_connection_string(self):
        # Create a mock config object
        mock_config = MagicMock()
        mock_config.provider = 'Azure'
        mock_config.connection_string = 'invalid_connection_string'

        with self.assertRaises(ValueError):
            # Create a Config instance with the mock config
            config = Config(config=mock_config)

            # Perform assertions (optional, if needed)
            self.assertEqual(config.provider, 'Azure')
            self.assertIsNone(config.client)
            self.assertIsNone(config.sender)

    @patch('logging.getLogger')
    def test_azure_provider_logging_levels(self, mock_get_logger):
        # Create a mock config object
        mock_config = MagicMock()
        mock_config.provider = 'Azure'
        mock_config.connection_string = 'valid_connection_string'
        mock_config.topic_name = 'mock_topic_name'

        # Create mock loggers
        mock_uamqp_logger = MagicMock()
        mock_uamqp_connection_logger = MagicMock()
        mock_get_logger.side_effect = [mock_uamqp_logger, mock_uamqp_connection_logger]

        with patch.object(ServiceBusClient, 'from_connection_string'):
            # Create a Config instance with the mock config
            config = Config(config=mock_config)

            # Perform assertions
            self.assertEqual(config.provider, 'Azure')
            self.assertEqual(config.connection_string, 'valid_connection_string')
            mock_get_logger.assert_any_call('uamqp')
            mock_get_logger.assert_any_call('uamqp.connection')
            mock_uamqp_logger.setLevel.assert_called_once_with(logging.ERROR)
            mock_uamqp_connection_logger.setLevel.assert_called_once_with(logging.ERROR)

    def test_sender_creation(self):
        # Create a mock config object
        mock_config = MagicMock()
        mock_config.provider = 'Azure'
        mock_config.connection_string = 'valid_connection_string'
        mock_config.topic_name = 'mock_topic_name'

        with patch.object(ServiceBusClient, 'from_connection_string'):
            # Create a Config instance with the mock config
            config = Config(config=mock_config)

            # Assert that the sender attribute is set with the ServiceBusMessage class
            self.assertEqual(config.sender, ServiceBusMessage)


if __name__ == '__main__':
    unittest.main()
