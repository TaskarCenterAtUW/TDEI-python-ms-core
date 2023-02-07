from .abstracts.logger_abstract import LoggerAbstract
from ..queue.models.queue_message import QueueMessage
from ..queue.queue import Queue


class LocalLogger(LoggerAbstract):

    def __init__(self, config=None):
        super().__init__(config=config)
        self.queue_client = Queue(config)

    def add_request(self, request_data):
        message = QueueMessage.data_from({
            'message': 'Add Request',
            'messageType': 'addRequest',
            'data': request_data
        })
        self.queue_client.send_local(message)

    def info(self, message: str):
        msg = QueueMessage.data_from({
            'message': message,
            'messageType': 'info',
        })
        self.queue_client.send_local(msg)

    def debug(self, message: str):
        msg = QueueMessage.data_from({
            'message': message,
            'messageType': 'debug',
        })
        self.queue_client.send_local(msg)

    def warn(self, message: str):
        msg = QueueMessage.data_from({
            'message': message,
            'messageType': 'warn',
        })
        self.queue_client.send_local(msg)

    def error(self, message: str):
        msg = QueueMessage.data_from({
            'message': message,
            'messageType': 'error',
        })
        self.queue_client.send_local(msg)

    def record_metric(self, name: str, value: str):
        message = QueueMessage.data_from({
            'message': 'metric',
            'messageType': 'metric',
            'data': {
                'name': name,
                'value': value
            }
        })
        self.queue_client.send_local(message)
