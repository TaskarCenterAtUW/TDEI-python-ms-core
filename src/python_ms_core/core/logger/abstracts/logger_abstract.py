from abc import ABC, abstractmethod


class LoggerAbstract(ABC):
    @abstractmethod
    def __init__(self, config=None): pass

    @abstractmethod
    def add_request(self, request_data):
        pass

    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def debug(self, message: str):
        pass

    @abstractmethod
    def warn(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass

    def record_metric(self, name: str, value: str):
        pass
