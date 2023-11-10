import json
import requests
from .config.queue_config import Config
from .models.queue_message import QueueMessage
from .abstracts.queue_abstract import QueueAbstract
from ..resource_errors import ExceptionHandler


class Queue(QueueAbstract):
    queue = list()

    def __init__(self, config):
        self.provider = Config(config=config)

    @ExceptionHandler.decorated
    def send(self, data=None):
        if data:
            message = QueueMessage.to_dict(data)
            with self.provider.client:
                sender = self.provider.client.get_queue_sender(queue_name=self.provider.queue_name)
                with sender:
                    sender.send_messages(self.provider.sender(json.dumps(message)))
        self.queue = list()

    def add(self, data):
        if data is not None:
            self.queue.insert(0, json.dumps(data))

    def remove(self):
        if len(self.queue) > 0:
            self.queue.pop()

    def get_items(self):
        return self.queue

    def empty(self):
        self.queue = list()
