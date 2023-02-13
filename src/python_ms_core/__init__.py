import logging
from .core.logger.logger import Logger
from .core.logger.local_logger import LocalLogger
from .core.topic.topic import Topic
from .core.topic.local_topic import LocalTopic
from .core.storage.providers.azure.azure_storage_client import AzureStorageClient
from .core.storage.providers.local.local_storage_client import LocalStorageClient
from .core.config.config import CoreConfig, LocalConfig

LOCAL_ENV = 'LOCAL'
AZURE_ENV = 'AZURE'


class Core:
    def __init__(self, config=None):
        if config is not None and config.upper() == LOCAL_ENV:
            self.config = LocalConfig()
        else:
            self.config = CoreConfig()
        self.__check_health()

    def get_logger(self):
        logger_config = self.config.logger()
        if logger_config.provider.upper() == LOCAL_ENV:
            return LocalLogger(config=logger_config)
        elif logger_config.provider.upper() == AZURE_ENV:
            return Logger(config=logger_config)
        else:
            logging.error(f'Unimplemented initialization for core {logger_config.provider}')

    def get_topic(self, topic_name: str):
        topic_config = self.config.topic()
        if topic_config.provider.upper() == LOCAL_ENV:
            return LocalTopic(config=topic_config, topic_name=topic_name)
        elif topic_config.provider.upper() == AZURE_ENV:
            return Topic(config=topic_config, topic_name=topic_name)
        else:
            logging.error(f'Unimplemented initialization for core {topic_config.provider}')

    def get_storage_client(self):
        storage_config = self.config.storage()
        if storage_config.provider.upper() == LOCAL_ENV:
            return LocalStorageClient(storage_config)
        elif storage_config.provider.upper() == AZURE_ENV:
            return AzureStorageClient(storage_config)
        else:
            logging.error(f'Unimplemented initialization for core {storage_config.provider}')

    def __check_health(self):
        print('\x1b[32m ------------------------- \x1b[0m')
        print('\x1b[30m\x1b[42m PERFORMING CORE-HEALTH-CHECK \x1b[0m')
        if self.config is None:
            print('Unknown/Unimplemented provider')
            print('\x1b[31m Unknown/Unimplemented provider. Please check the provider supplied \x1b[0m')
            print('\x1b[33m Valid providers are \x1b[0m')
            print('\x1b[32m Azure \x1b[0m')
            return False

        print(f'Configured for \x1b[32m {self.config.provider} \x1b[0m \n')

        logger_config = self.config.logger()
        queue_config = self.config.queue()
        storage_config = self.config.storage()
        logger_queue_name = logger_config.queue_name
        queue_connection = queue_config.connection_string
        storage_connection = storage_config.connection_string
        print('\x1b[31m > Checking Queue Connections\x1b[0m')
        if queue_connection is None:
            print('\x1b[33m Queue connection not available by default \x1b[0m')
            print('\x1b[33m Please configure QUEUECONNECTION in .env file to ensure queue communication \x1b[0m')
            print('\x1b[33m Note: All the logger functionality will be restricted to console \x1b[0m')
        else:
            print('\x1b[32m\x1b[40m Connected to Queues \x1b[0m')

        print('\x1b[31m\n > Checking Storage Connections\x1b[0m')

        if storage_connection is None:
            print('\x1b[31m Storage connection not available \x1b[0m')
            print('\x1b[31m Storage related functionalities will be unavailable \x1b[0m')
            print('\x1b[31m Please configure STORAGECONNECTION in .env for storage functions \x1b[0m')
        else:
            print('\x1b[32m\x1b[40m Connected to Storage \x1b[0m')

        print('\x1b[31m\n > Checking Logger Queue \x1b[0m')
        if logger_queue_name is None:
            print('\x1b[33m Logger queue is not configured. App will write to  \x1b[0m')
            print('\x1b[32m tdei-ms-log queue \x1b[0m')
        else:
            print('\x1b[32m Logger configured \x1b[0m')
        print('\x1b[32m ------------------------- \x1b[0m')
        return True
