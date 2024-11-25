import os
import unittest
from unittest.mock import patch
from src.python_ms_core.core.storage.models.config import CoreConfig



class TestCoreConfig(unittest.TestCase):

    @patch.dict(os.environ, {'PROVIDER': 'AWS'})  # Mocking the environment variable
    def test_provider_set_from_env(self):
        # Initialize CoreConfig with mocked PROVIDER environment variable
        config = CoreConfig()

        # Assertions
        self.assertEqual(config.provider, 'AWS', "Expected provider to be 'AWS' based on environment variable.")

    @patch.dict(os.environ, {})  # Mocking the environment without PROVIDER
    def test_provider_default_to_azure(self):
        # Initialize CoreConfig with no PROVIDER environment variable
        config = CoreConfig()

        # Assertions
        self.assertEqual(config.provider, 'Azure', "Expected provider to default to 'Azure' when not set.")

    def test_default_method_returns_core_config(self):
        # Test that the default method returns an instance of CoreConfig
        config = CoreConfig.default()

        # Assertions
        self.assertIsInstance(config, CoreConfig, "Expected CoreConfig.default() to return an instance of CoreConfig.")
        self.assertEqual(config.provider, 'Azure', "Expected default provider to be 'Azure'.")


if __name__ == "__main__":
    unittest.main()
