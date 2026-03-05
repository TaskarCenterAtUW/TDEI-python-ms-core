from abc import ABC, abstractmethod


class TopicAbstract(ABC):
    @abstractmethod
    def __init__(self, config=None, topic_name=None): pass

    @abstractmethod
    def subscribe(self, subscription=None, callback=None, max_receivable_messages=-1): pass

    @abstractmethod
    def publish(self, data=None): pass