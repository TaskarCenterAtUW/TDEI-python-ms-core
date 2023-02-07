import os
from dotenv import load_dotenv

load_dotenv()


class LogerConfig:
    def __init__(self, provider: str, con_string: str, queue_name: str):
        self.provider = provider
        self.connection_string = con_string
        self.queue_name = queue_name


class QueueConfig:
    def __init__(self, provider: str, con_string: str, queue_name: str):
        self.provider = provider
        self.connection_string = con_string
        self.queue_name = queue_name


class TopicConfig:
    def __init__(self, provider: str, con_string: str):
        self.provider = provider
        self.connection_string = con_string


class StorageConfig:
    def __init__(self, provider: str, con_string: str):
        self.provider = provider
        self.connection_string = con_string


class CoreConfig:
    def __init__(self):
        self.provider = os.environ.get('PROVIDER', 'Azure')
        self.queue_connection = os.environ.get('QUEUECONNECTION', None)
        self.queue_name = os.environ.get('LOGGERQUEUE', 'tdei-ms-log')
        self.topic_connection = os.environ.get('QUEUECONNECTION', None)
        self.storage_connection = os.environ.get('STORAGECONNECTION', None)

    def logger(self):
        return LogerConfig(
            provider=self.provider,
            con_string=self.queue_connection,
            queue_name=self.queue_name
        )

    def queue(self):
        return QueueConfig(
            provider=self.provider,
            con_string=self.queue_connection,
            queue_name=self.queue_name
        )

    def topic(self):
        return TopicConfig(
            provider=self.provider,
            con_string=self.topic_connection
        )

    def storage(self):
        return StorageConfig(
            provider=self.provider,
            con_string=self.storage_connection
        )


class LocalConfig:
    def __init__(self):
        self.provider = 'local'

    def logger(self):
        return LogerConfig(
            provider=self.provider,
            con_string='amqp://guest:guest@rabbitmq:5672/',
            queue_name='http://localhost:8100'
        )

    def queue(self):
        return QueueConfig(
            provider=self.provider,
            con_string='amqp://guest:guest@rabbitmq:5672/',
            queue_name='http://localhost:8100'
        )

    def topic(self):
        return TopicConfig(
            provider=self.provider,
            con_string='amqp://guest:guest@rabbitmq:5672/'
        )

    def storage(self):
        return StorageConfig(
            provider=self.provider,
            con_string='http://localhost:8100'
        )
