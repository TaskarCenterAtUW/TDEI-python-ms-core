from abc import ABC, abstractmethod


class StorageContainer(ABC):
    @abstractmethod
    def __init__(self, name):
        self.name = name
        pass

    @abstractmethod
    def list_files(self):
        pass

    @abstractmethod
    def create_file(self, name, mimetype):
        pass
