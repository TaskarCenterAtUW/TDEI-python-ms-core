from abc import ABC, abstractmethod


class StorageClient(ABC):
    @abstractmethod
    def get_container(self, name: str): pass

    @abstractmethod
    def get_file(self, container_name: str, file_name: str): pass

    @abstractmethod
    def get_file_from_url(self, container_name: str, full_url: str): pass

