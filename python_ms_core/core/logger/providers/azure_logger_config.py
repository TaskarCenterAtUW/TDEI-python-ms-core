import os
from dotenv import load_dotenv
from .provider import Provider

load_dotenv()


class AzureQueueConfig:
    provider = Provider()

    def __init__(self):
        self.logger_queue_name = os.environ.get('LOGGERQUEUE', 'tdei-ms-log')
