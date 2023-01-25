from abc import ABC, abstractmethod


class FileEntity(ABC):
    name = ''
    file_path = ''

    @abstractmethod
    def __init__(self, name: str):
        self.name = name
        self.file_path = name
        pass

    @abstractmethod
    def get_stream(self):
        pass

    @abstractmethod
    def get_body_text(self):
        pass

    @abstractmethod
    def upload(self, upload_stream):
        pass

    @abstractmethod
    def get_remote_url(self):
        pass
