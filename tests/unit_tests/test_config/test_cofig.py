import os
from dotenv import load_dotenv
import unittest
from unittest.mock import patch
from src.python_ms_core.core.config.config import CoreConfig, LocalConfig, UnknownConfig, QueueConfig, TopicConfig, \
    StorageConfig, AuthConfig, LogerConfig

load_dotenv()


class TestCoreConfig(unittest.TestCase):

    def tearDown(self):
        os.environ.clear()

    def test_core_config_provider(self):
        os.environ['PROVIDER'] = 'Azure'
        config = CoreConfig()
        self.assertEqual(config.provider, 'Azure')

    def test_core_config_provider_default(self):
        config = CoreConfig()
        self.assertEqual(config.provider, 'Azure')

    def test_core_config_provider_override(self):
        os.environ['PROVIDER'] = 'CustomProvider'
        config = CoreConfig()
        self.assertEqual(config.provider, 'CustomProvider')

    def test_core_config_queue_connection(self):
        os.environ['QUEUECONNECTION'] = 'amqp://guest:guest@localhost:5672'
        config = CoreConfig()
        self.assertEqual(config.queue_connection, 'amqp://guest:guest@localhost:5672')
        del os.environ['QUEUECONNECTION']

    def test_core_config_queue_connection_default(self):
        config = CoreConfig()
        self.assertIsNone(config.queue_connection)

    def test_core_config_queue_name(self):
        os.environ['LOGGERQUEUE'] = 'custom_queue'
        config = CoreConfig()
        self.assertEqual(config.queue_name, 'custom_queue')

    def test_core_config_queue_name_default(self):
        config = CoreConfig()
        self.assertEqual(config.queue_name, 'tdei-ms-log')

    def test_core_config_topic_connection(self):
        os.environ['QUEUECONNECTION'] = 'amqp://guest:guest@localhost:5672'
        config = CoreConfig()
        self.assertEqual(config.topic_connection, 'amqp://guest:guest@localhost:5672')

    def test_core_config_topic_connection_default(self):
        config = CoreConfig()
        self.assertIsNone(config.topic_connection)

    def test_core_config_storage_connection(self):
        os.environ['STORAGECONNECTION'] = 'http://localhost:8100'
        config = CoreConfig()
        self.assertEqual(config.storage_connection, 'http://localhost:8100')

    def test_core_config_storage_connection_default(self):
        config = CoreConfig()
        self.assertIsNone(config.storage_connection)

    def test_core_config_auth_url(self):
        os.environ['AUTHURL'] = 'http://auth-url.com'
        config = CoreConfig()
        self.assertEqual(config.auth_url, 'http://auth-url.com')

    def test_core_config_auth_url_default(self):
        config = CoreConfig()
        self.assertIsNone(config.auth_url)

    def test_core_config_logger(self):
        config = CoreConfig()
        logger_config = config.logger()
        self.assertIsInstance(logger_config, LogerConfig)
        self.assertEqual(logger_config.provider, config.provider)
        self.assertEqual(logger_config.connection_string, config.queue_connection)
        self.assertEqual(logger_config.queue_name, config.queue_name)

    def test_core_config_queue(self):
        config = CoreConfig()
        queue_config = config.queue()
        self.assertIsInstance(queue_config, QueueConfig)
        self.assertEqual(queue_config.provider, config.provider)
        self.assertEqual(queue_config.connection_string, config.queue_connection)
        self.assertEqual(queue_config.queue_name, config.queue_name)

    def test_core_config_topic(self):
        config = CoreConfig()
        topic_config = config.topic()
        self.assertIsInstance(topic_config, TopicConfig)
        self.assertEqual(topic_config.provider, config.provider)
        self.assertEqual(topic_config.connection_string, config.topic_connection)

    def test_core_config_storage(self):
        config = CoreConfig()
        storage_config = config.storage()
        self.assertIsInstance(storage_config, StorageConfig)
        self.assertEqual(storage_config.provider, config.provider)
        self.assertEqual(storage_config.connection_string, config.storage_connection)

    def test_core_config_auth(self):
        os.environ['AUTHURL'] = 'http://auth-url.com'
        config = CoreConfig()
        auth_config = config.auth()
        self.assertIsInstance(auth_config, AuthConfig)
        self.assertEqual(auth_config.provider, 'Hosted')
        self.assertEqual(auth_config.auth_url, config.auth_url)


class TestLocalConfig(unittest.TestCase):

    def tearDown(self):
        os.environ.clear()

    def test_local_config_provider(self):
        os.environ['PROVIDER'] = 'local'
        config = LocalConfig()
        self.assertEqual(config.provider, 'local')

    def test_local_config_provider_default(self):
        config = LocalConfig()
        self.assertEqual(config.provider, 'local')

    def test_local_config_queue_connection(self):
        os.environ['QUEUECONNECTION'] = 'amqp://guest:guest@localhost:5672'
        config = LocalConfig()
        self.assertEqual(config.queue_connection, 'amqp://guest:guest@localhost:5672')

    def test_local_config_queue_connection_default(self):
        config = LocalConfig()
        self.assertEqual(config.queue_connection, 'amqp://guest:guest@localhost:5672')

    def test_local_config_queue_name(self):
        os.environ['LOGGERQUEUE'] = 'custom_queue'
        config = LocalConfig()
        self.assertEqual(config.queue_name, 'custom_queue')

    def test_local_config_queue_name_default(self):
        config = LocalConfig()
        self.assertEqual(config.queue_name, 'http://localhost:8100')

    def test_local_config_topic_connection(self):
        os.environ['QUEUECONNECTION'] = 'amqp://guest:guest@localhost:5672'
        config = LocalConfig()
        self.assertEqual(config.topic_connection, 'amqp://guest:guest@localhost:5672')

    def test_local_config_topic_connection_default(self):
        config = LocalConfig()
        self.assertEqual(config.topic_connection, 'amqp://guest:guest@localhost:5672')

    def test_local_config_storage_connection(self):
        os.environ['STORAGECONNECTION'] = 'http://localhost:8100'
        config = LocalConfig()
        self.assertEqual(config.storage_connection, 'http://localhost:8100')

    def test_local_config_storage_connection_default(self):
        config = LocalConfig()
        self.assertEqual(config.storage_connection, 'http://localhost:8100')

    def test_local_config_logger(self):
        config = LocalConfig()
        logger_config = config.logger()
        self.assertIsInstance(logger_config, LogerConfig)
        self.assertEqual(logger_config.provider, config.provider)
        self.assertEqual(logger_config.connection_string, config.queue_connection)
        self.assertEqual(logger_config.queue_name, config.queue_name)

    def test_local_config_queue(self):
        config = LocalConfig()
        queue_config = config.queue()
        self.assertIsInstance(queue_config, QueueConfig)
        self.assertEqual(queue_config.provider, config.provider)
        self.assertEqual(queue_config.connection_string, config.queue_connection)
        self.assertEqual(queue_config.queue_name, config.queue_name)

    def test_local_config_topic(self):
        config = LocalConfig()
        topic_config = config.topic()
        self.assertIsInstance(topic_config, TopicConfig)
        self.assertEqual(topic_config.provider, config.provider)
        self.assertEqual(topic_config.connection_string, config.topic_connection)

    def test_local_config_storage(self):
        config = LocalConfig()
        storage_config = config.storage()
        self.assertIsInstance(storage_config, StorageConfig)
        self.assertEqual(storage_config.provider, config.provider)
        self.assertEqual(storage_config.connection_string, config.storage_connection)

    def test_local_config_auth(self):
        config = LocalConfig()
        auth_config = config.auth()
        self.assertIsInstance(auth_config, AuthConfig)
        self.assertEqual(auth_config.provider, 'Simulated')


class TestUnknownConfig(unittest.TestCase):

    def test_unknown_config_provider(self):
        config = UnknownConfig('CustomProvider')
        self.assertEqual(config.provider, 'CustomProvider')

    def test_unknown_config_queue_connection_default(self):
        config = UnknownConfig('CustomProvider')
        self.assertIsNone(config.queue_connection)

    def test_unknown_config_queue_name_default(self):
        config = UnknownConfig('CustomProvider')
        self.assertIsNone(config.queue_name)

    def test_unknown_config_topic_connection_default(self):
        config = UnknownConfig('CustomProvider')
        self.assertIsNone(config.topic_connection)

    def test_unknown_config_storage_connection_default(self):
        config = UnknownConfig('CustomProvider')
        self.assertIsNone(config.storage_connection)

    def test_unknown_config_logger(self):
        config = UnknownConfig('CustomProvider')
        logger_config = config.logger()
        self.assertIsInstance(logger_config, LogerConfig)
        self.assertEqual(logger_config.provider, config.provider)
        self.assertEqual(logger_config.connection_string, config.queue_connection)
        self.assertEqual(logger_config.queue_name, config.queue_name)

    def test_unknown_config_queue(self):
        config = UnknownConfig('CustomProvider')
        queue_config = config.queue()
        self.assertIsInstance(queue_config, QueueConfig)
        self.assertEqual(queue_config.provider, config.provider)
        self.assertEqual(queue_config.connection_string, config.queue_connection)
        self.assertEqual(queue_config.queue_name, config.queue_name)

    def test_unknown_config_topic(self):
        config = UnknownConfig('CustomProvider')
        topic_config = config.topic()
        self.assertIsInstance(topic_config, TopicConfig)
        self.assertEqual(topic_config.provider, config.provider)
        self.assertEqual(topic_config.connection_string, config.topic_connection)

    def test_unknown_config_storage(self):
        config = UnknownConfig('CustomProvider')
        storage_config = config.storage()
        self.assertIsInstance(storage_config, StorageConfig)
        self.assertEqual(storage_config.provider, config.provider)
        self.assertEqual(storage_config.connection_string, config.storage_connection)

    def test_local_config_auth(self):
        config = UnknownConfig('CustomProvider')
        auth_config = config.auth()
        self.assertIsInstance(auth_config, AuthConfig)
        self.assertEqual(auth_config.provider, 'Simulated')


if __name__ == '__main__':
    unittest.main()
