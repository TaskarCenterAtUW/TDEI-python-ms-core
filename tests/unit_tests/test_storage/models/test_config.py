import unittest
from unittest.mock import patch
import os


class CoreConfig:
    def __init__(self):
        self.provider = os.environ.get('PROVIDER', 'Azure')

    @staticmethod
    def default():
        return CoreConfig()


class TestCoreConfig(unittest.TestCase):
    @patch('os.environ.get')
    def test_init_with_default_provider(self, mock_env_get):
        # Test case for initializing CoreConfig with default provider
        mock_env_get.return_value = 'Azure'
        config = CoreConfig()
        self.assertEqual(config.provider, 'Azure')

    @patch('os.environ.get')
    def test_init_with_custom_provider(self, mock_env_get):
        # Test case for initializing CoreConfig with custom provider
        custom_provider = 'AWS'
        mock_env_get.return_value = custom_provider
        config = CoreConfig()
        self.assertEqual(config.provider, custom_provider)

    @patch('os.environ.get')
    def test_default_method(self, mock_env_get):
        # Test case for default method of CoreConfig
        mock_env_get.return_value = 'Azure'
        config = CoreConfig.default()
        self.assertIsInstance(config, CoreConfig)
        self.assertEqual(config.provider, 'Azure')


if __name__ == "__main__":
    unittest.main()
