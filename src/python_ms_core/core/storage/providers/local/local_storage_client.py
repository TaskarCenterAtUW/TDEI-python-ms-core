import logging
import urllib.parse
from .local_storage_container import LocalStorageContainer
from .local_file_entity import LocalFileEntity
from ...abstract.storage_client import StorageClient
from ....resource_errors import ExceptionHandler


class LocalStorageClient(StorageClient):
    def __init__(self, config):
        super().__init__()
        self.config = config

    @ExceptionHandler.decorated
    def get_container(self, container_name: str):
        if container_name:
            return LocalStorageContainer(config=self.config, name=container_name)
        else:
            logging.error(f'Unimplemented initialize for core {self.config.provider}, Container name is required!')
            return

    @ExceptionHandler.decorated
    def get_file(self, container_name: str, file_name: str):
        return LocalFileEntity('uploadFile', f'{container_name}/{file_name}', config=self.config)

    @ExceptionHandler.decorated
    def get_file_from_url(self, container_name: str, full_url: str):
        path = '/'.join(urllib.parse.unquote(full_url).split('/')[5:])
        file = LocalFileEntity
        client = LocalStorageContainer(config=self.config, name=container_name)
        files = client.list_files()
        for file_info in files:
            if file_info.path == path:
                file = file_info
        return file
