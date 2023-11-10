import json
from datetime import datetime
from typing import Union, List
from dataclasses import dataclass
from ...resource_errors import ExceptionHandler


class Validations:
    def __post_init__(self):
        for name, field in self.__dataclass_fields__.items():
            fn_name = 'validate_data' if name == 'data' else 'validate_string'
            if method := getattr(self, f'{fn_name}', None):
                setattr(self, name, method(getattr(self, name), field=field))


@dataclass
class QueueMessage(Validations):
    message: str = ''
    messageId: str = ''
    messageType: str = ''
    publishedDate: str = str(datetime.now())
    data: Union[dict, List[dict]] = dict
    queue = list()

    def add(self, data=None):
        if data is not None:
            self.queue.insert(0, json.dumps(data))
            return True
        return False

    def empty(self):
        self.queue = list()

    def remove(self):
        if len(self.queue) > 0:
            self.queue.pop()
        return True

    def send(self):
        self.queue = list()
        return True

    def get_items(self):
        return [json.loads(item) for item in self.queue]

    @ExceptionHandler.decorated
    def data_from(self):
        data = self
        if isinstance(data, str):
            data = json.loads(self)

        kwargs = {}
        if data:
            for key, value in data.items():
                if value:
                    kwargs[key] = value
            try:
                return QueueMessage(**kwargs)
            except Exception as e:
                error = str(e).replace('QueueMessage', 'Invalid parameter,')
                error = error.replace('__init__()', 'QueueMessage')
                raise TypeError(f'{error} \nStatus code: 400')

    def to_dict(self):
        if isinstance(self, QueueMessage):
            return self.__dict__
        else:
            return self

    def validate_string(self, value, **_):
        name = _.get('field').name
        if isinstance(value, str):
            return value

        raise ValueError(f'{name} must be a string.')

    def validate_data(self, value, **_):
        name = _.get('field').name
        if isinstance(value, type):
            value = {}
        if isinstance(value, dict) or isinstance(value, list) or isinstance(value, type):
            return value
        raise ValueError(f'{name} must be an object.')
