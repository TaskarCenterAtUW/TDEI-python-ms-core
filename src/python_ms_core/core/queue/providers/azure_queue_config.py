import os
from dotenv import load_dotenv
from ..models.config import CoreConfig

load_dotenv()


class AzureQueueConfig:
    def __init__(self):
        config = CoreConfig.default()
        self.provider = config.provider
        self.connection_string = os.environ.get('QUEUECONNECTION', '')
