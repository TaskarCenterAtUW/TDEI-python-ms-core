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


class AuthConfig:
    def __init__(self, provider: str, auth_url: str = None):
        self.provider = provider
        self.auth_url = auth_url


class CoreConfig:
    def __init__(self):
        self.provider = os.environ.get('PROVIDER', 'Azure')
        self.queue_connection = os.environ.get('QUEUECONNECTION', None)
        self.queue_name = os.environ.get('LOGGERQUEUE', 'tdei-ms-log')
        self.topic_connection = os.environ.get('QUEUECONNECTION', None)
        self.storage_connection = os.environ.get('STORAGECONNECTION', None)
        self.auth_url = os.environ.get('AUTHURL', None)

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

    def auth(self):
        return AuthConfig(
            provider='Hosted',
            auth_url=self.auth_url
        )


class LocalConfig:
    def __init__(self):
        self.provider = os.environ.get('PROVIDER', 'local')
        self.queue_connection = os.environ.get('QUEUECONNECTION', 'amqp://guest:guest@localhost:5672')
        self.queue_name = os.environ.get('LOGGERQUEUE', 'http://localhost:8100')
        self.topic_connection = os.environ.get('QUEUECONNECTION', 'amqp://guest:guest@localhost:5672')
        self.storage_connection = os.environ.get('STORAGECONNECTION', 'http://localhost:8100')

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

    def auth(self):
        return AuthConfig(
            provider='Simulated'
        )


class UnknownConfig:
    def __init__(self, provider: str):
        self.provider = provider
        self.queue_connection = None
        self.queue_name = None
        self.topic_connection = None
        self.storage_connection = None

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

    def auth(self):
        return AuthConfig(
            provider='Simulated'
        )

