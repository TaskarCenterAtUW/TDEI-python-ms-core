import os
import unittest
from unittest.mock import patch
from src.python_ms_core.core.config.config import CoreConfig, LocalConfig


class TestCoreConfig(unittest.TestCase):
    def test_logger(self):
        with patch.dict(os.environ, {'PROVIDER': 'MockProvider', 'QUEUECONNECTION': 'MockConnectionString',
                                     'LOGGERQUEUE': 'MockQueue'}):
            config = CoreConfig()
            logger_config = config.logger()

            self.assertEqual(logger_config.provider, 'MockProvider')
            self.assertEqual(logger_config.connection_string, 'MockConnectionString')
            self.assertEqual(logger_config.queue_name, 'MockQueue')

    def test_queue(self):
        with patch.dict(os.environ, {'PROVIDER': 'MockProvider', 'QUEUECONNECTION': 'MockConnectionString',
                                     'LOGGERQUEUE': 'MockQueue'}):
            config = CoreConfig()
            queue_config = config.queue()
            self.assertEqual(queue_config.provider, 'MockProvider')
            self.assertEqual(queue_config.connection_string, 'MockConnectionString')
            self.assertEqual(queue_config.queue_name, 'MockQueue')

    def test_topic(self):
        with patch.dict(os.environ, {'PROVIDER': 'MockProvider', 'QUEUECONNECTION': 'MockConnectionString'}):
            config = CoreConfig()
            topic_config = config.topic()
            self.assertEqual(topic_config.provider, 'MockProvider')
            self.assertEqual(topic_config.connection_string, 'MockConnectionString')

    def test_storage(self):
        with patch.dict(os.environ, {'PROVIDER': 'MockProvider', 'STORAGECONNECTION': 'MockConnectionString'}):
            config = CoreConfig()
            storage_config = config.storage()
            self.assertEqual(storage_config.provider, 'MockProvider')
            self.assertEqual(storage_config.connection_string, 'MockConnectionString')

    def test_auth(self):
        with patch.dict(os.environ, {'PROVIDER': 'Hosted', 'AUTHURL': 'https://example.com/api/auth'}):
            config = CoreConfig()
            auth_config = config.auth()
            self.assertEqual(auth_config.provider, 'Hosted')
            self.assertEqual(auth_config.auth_url, 'https://example.com/api/auth')


class TestLocalConfig(unittest.TestCase):
    def test_logger(self):
        with patch.dict(os.environ, {'PROVIDER': 'MockProvider', 'QUEUECONNECTION': 'MockConnectionString',
                                     'LOGGERQUEUE': 'MockQueue'}):
            config = LocalConfig()
            logger_config = config.logger()

            self.assertEqual(logger_config.provider, 'MockProvider')
            self.assertEqual(logger_config.connection_string, 'MockConnectionString')
            self.assertEqual(logger_config.queue_name, 'MockQueue')

    def test_queue(self):
        with patch.dict(os.environ, {'PROVIDER': 'MockProvider', 'QUEUECONNECTION': 'MockConnectionString',
                                     'LOGGERQUEUE': 'MockQueue'}):
            config = LocalConfig()
            queue_config = config.queue()
            self.assertEqual(queue_config.provider, 'MockProvider')
            self.assertEqual(queue_config.connection_string, 'MockConnectionString')
            self.assertEqual(queue_config.queue_name, 'MockQueue')

    def test_topic(self):
        with patch.dict(os.environ, {'PROVIDER': 'MockProvider', 'QUEUECONNECTION': 'MockConnectionString'}):
            config = LocalConfig()
            topic_config = config.topic()
            self.assertEqual(topic_config.provider, 'MockProvider')
            self.assertEqual(topic_config.connection_string, 'MockConnectionString')

    def test_storage(self):
        with patch.dict(os.environ, {'PROVIDER': 'MockProvider', 'STORAGECONNECTION': 'MockConnectionString'}):
            config = LocalConfig()
            storage_config = config.storage()
            self.assertEqual(storage_config.provider, 'MockProvider')
            self.assertEqual(storage_config.connection_string, 'MockConnectionString')

    def test_auth(self):
        with patch.dict(os.environ, {'PROVIDER': 'Simulated'}):
            config = LocalConfig()
            auth_config = config.auth()
            self.assertEqual(auth_config.provider, 'Simulated')


if __name__ == '__main__':
    unittest.main()
