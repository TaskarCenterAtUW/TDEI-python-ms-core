import logging
import os
from dotenv import load_dotenv

from models.abstracts.iconfig import IConfig
from core.logger.logger import Logger
from core.queue import topic
from models.config import CoreConfig

load_dotenv()


class Core:

    def __init__(self):
        self.config = CoreConfig.default()

        if self.config.provider == 'Local':
            logging.error(f'Unimplemented initialization for core {self.config.provider}')

    @staticmethod
    def initialize():
        return Core().__check_health()

    @staticmethod
    def get_topic(topic_name):

        queue_config = CoreConfig.default()
        print(queue_config.provider)
        return topic.Topic(queue_config, topic_name)

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

        if self.config.provider == 'Azure':
            logger_queue_name = os.environ.get('LOGGERQUEUE', None)
            queue_connection = os.environ.get('QUEUECONNECTION', None)
            storage_connection = os.environ.get('STORAGECONNECTION', None)

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
        return True
