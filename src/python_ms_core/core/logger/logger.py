import logging
from .providers.azure_logger_config import AzureLoggerConfig
from ..queue.models.queue_message import QueueMessage
from ..queue.queue import Queue
from .abstracts.logger_abstract import LoggerAbstract


class Logger(LoggerAbstract):

    def __init__(self, queue_name=None):
        super().__init__(queue_name=queue_name)
        self.config = AzureLoggerConfig()
        if queue_name is None:
            logging.error(f'Unimplemented initialization for core {self.config.provider}, Queue name is required!')
            return
        else:
            self.queue_client = Queue(self.config, queue_name=queue_name)

    def add_request(self, request_data):
        message = QueueMessage.data_from({
            'message': 'Add Request',
            'messageType': 'addRequest',
            'data': request_data
        })
        self.queue_client.send(message)

    def info(self, message: str):
        msg = QueueMessage.data_from({
            'message': message,
            'messageType': 'info',
        })
        self.queue_client.send(msg)

    def debug(self, message: str):
        msg = QueueMessage.data_from({
            'message': message,
            'messageType': 'debug',
        })
        self.queue_client.send(msg)

    def record_metric(self, name: str, value: str):
        message = QueueMessage.data_from({
            'message': 'metric',
            'messageType': 'metric',
            'data': {
                'name': name,
                'value': value
            }
        })
        self.queue_client.send(message)
