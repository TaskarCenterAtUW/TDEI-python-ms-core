import json
import requests
from .config.queue_config import Config
from .models.queue_message import QueueMessage
from .abstracts.queue_abstract import QueueAbstract
from ..resource_errors import ExceptionHandler


class LocalQueue(QueueAbstract):
    queue = list()

    def __init__(self, config):
        self.provider = Config(config=config)

    @ExceptionHandler.decorated
    def send(self, data=None):
        if data:
            message = QueueMessage.to_dict(data)
            url = f'{self.provider.queue_name}/log'
            try:
                resp = requests.post(url, json=message)
                print(resp.status_code)
            except Exception as e:
                print(e)
                print(message)

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
