import os
from dotenv import load_dotenv
from .provider import Provider

load_dotenv()


class AzureLoggerConfig:
    provider = Provider()
    logger_queue_name = None

    def __init__(self, provider_config=None):
        self.provider = provider_config or self.provider
        self.connection_string = os.environ.get('QUEUECONNECTION', '')
