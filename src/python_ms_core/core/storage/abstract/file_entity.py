from abc import ABC, abstractmethod


class FileEntity(ABC):
    name = ''
    mimetype = 'text/plain'
    file_path = ''

    @abstractmethod
    def __init__(self, name: str, mimetype: str = 'text/plain'):
        self.name = name
        self.mimetype = mimetype
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
