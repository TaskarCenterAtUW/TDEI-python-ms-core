import requests
from io import StringIO
from ...abstract.file_entity import FileEntity
from ....resource_errors import ExceptionHandler


class LocalFileEntity(FileEntity):

    def __init__(self, name, path, config=None):
        super().__init__(name)
        self._get_remote_url = None
        self.download_path = '/files/download/'
        self.upload_path = '/files/upload/'
        self.config = config
        self.path = path or None

    @ExceptionHandler.decorated
    def get_stream(self):
        download_relative_path = f'{self.config.connection_string}{self.download_path}{self.path}'
        response = requests.get(download_relative_path, stream=True)
        return response.text

    @ExceptionHandler.decorated
    def get_body_text(self):
        return StringIO(self.get_stream()).read()

    @ExceptionHandler.decorated
    def upload(self, upload_stream):
        upload_path = f'{self.path}/{self.name}'
        upload_relative_path = f'{self.config.connection_string}{self.upload_path}{upload_path}'
        requests.post(upload_relative_path, files={'uploadFile': upload_stream})
        self._get_remote_url = upload_relative_path

    @ExceptionHandler.decorated
    def get_remote_url(self):
        return self._get_remote_url
