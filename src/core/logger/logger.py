from .providers.azure_logger_config import AzureQueueConfig


class Logger:
    def __init__(self):
        config = AzureQueueConfig()
        print(config.provider)
        print(config.logger_queue_name)
        print('hello')
