from abc import ABC, abstractmethod


class LoggerAbstract(ABC):
    @abstractmethod
    def __init__(self, provider_config=None, queue_name=None): pass

    @abstractmethod
    def add_request(self, request_data):
        pass

    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def debug(self, message: str):
        pass

    def record_metric(self, name: str, value: str):
        pass
