from abc import ABC, abstractmethod


class QueueAbstract(ABC):
    @abstractmethod
    def __init__(self, config): pass

    @abstractmethod
    def send(self, data=None): pass

    @abstractmethod
    def add(self, data): pass

    @abstractmethod
    def remove(self): pass

    @abstractmethod
    def get_items(self): pass
