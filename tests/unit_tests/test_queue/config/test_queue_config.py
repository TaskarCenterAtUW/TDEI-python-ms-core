import unittest
from unittest.mock import MagicMock, patch
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from src.python_ms_core.core.queue.config.queue_config import Config


class TestConfig(unittest.TestCase):
    def test_non_azure_provider(self):
        # Create a mock config object
        mock_config = MagicMock()
        mock_config.provider = 'NonAzure'
        mock_config.queue_name = None

        # Create a Config instance with the mock config
        config = Config(config=mock_config)

        # Perform assertions
        self.assertEqual(config.provider, 'NonAzure')
        self.assertIsNone(config.queue_name)
        self.assertFalse(hasattr(config, 'client'))  # Check if 'client' attribute is absent
        self.assertFalse(hasattr(config, 'sender'))  # Check if 'sender' attribute is absent

    def test_azure_provider_valid_connection_string(self):
        # Create a mock config object
        mock_config = MagicMock()
        mock_config.provider = 'Azure'
        mock_config.connection_string = 'valid_connection_string'
        mock_config.queue_name = 'mock_queue_name'

        # Mock the ServiceBusClient.from_connection_string method
        with patch.object(ServiceBusClient, 'from_connection_string') as mock_from_connection_string:
            # Create a Config instance with the mock config
            config = Config(config=mock_config)

            # Perform assertions
            self.assertEqual(config.provider, 'Azure')
            self.assertEqual(config.connection_string, 'valid_connection_string')
            self.assertEqual(config.queue_name, 'mock_queue_name')
            mock_from_connection_string.assert_called_once_with(
                conn_str='valid_connection_string', logging_enable=False, retry_total=0
            )

    def test_azure_provider_invalid_connection_string(self):
        # Create a mock config object
        mock_config = MagicMock()
        mock_config.provider = 'Azure'
        mock_config.connection_string = 'invalid_connection_string'
        mock_config.queue_name = 'mock_queue_name'

        with self.assertRaises(ValueError):
            # Create a Config instance with the mock config
            config = Config(config=mock_config)

            # Perform assertions (optional, if needed)
            self.assertEqual(config.provider, 'Azure')
            self.assertEqual(config.queue_name, 'mock_queue_name')
            self.assertIsNone(config.client)
            self.assertIsNone(config.sender)

    @patch('azure.servicebus.ServiceBusMessage', autospec=True)
    def test_azure_provider_missing_queue_name(self, mock_message):
        # Create a mock config object
        mock_config = MagicMock()
        mock_config.provider = 'Azure'
        mock_config.connection_string = 'valid_connection_string'
        mock_config.queue_name = None

        # Mock the ServiceBusClient.from_connection_string method
        with patch.object(ServiceBusClient, 'from_connection_string', return_value=None) as mock_from_connection_string:
            # Create a Config instance with the mock config
            config = Config(config=mock_config)

            # Perform assertions
            self.assertEqual(config.provider, 'Azure')
            self.assertIsNone(config.queue_name)
            self.assertIsNone(config.client)

            # Verify that ServiceBusClient.from_connection_string is called with the expected arguments
            mock_from_connection_string.assert_called_once_with(
                conn_str=mock_config.connection_string, logging_enable=False, retry_total=0
            )

            # Verify that ServiceBusMessage is not called
            mock_message.assert_not_called()


if __name__ == '__main__':
    unittest.main()
