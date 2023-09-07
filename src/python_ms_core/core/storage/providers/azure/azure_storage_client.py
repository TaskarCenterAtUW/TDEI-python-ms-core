import logging
import urllib.parse
from azure.storage.blob import BlobServiceClient
from . import azure_file_entity, azure_storage_container
from ...abstract import storage_client
from ....resource_errors import ExceptionHandler


class AzureStorageClient(storage_client.StorageClient):
    _blob_service_client: BlobServiceClient

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._blob_service_client = BlobServiceClient.from_connection_string(config.connection_string)

    @ExceptionHandler.decorated
    def get_container(self, container_name: str):
        if container_name:
            client_container = self._blob_service_client.get_container_client(container_name)
            return azure_storage_container.AzureStorageContainer(container_name, client_container)
        else:
            logging.error(f'Unimplemented initialize for core {self.config.provider}, Container name is required!')
            return

    @ExceptionHandler.decorated
    def get_file(self, container_name: str, file_name: str):
        client_container = self._blob_service_client.get_container_client(container_name)
        blob_client = client_container.get_blob_client(file_name)
        return azure_file_entity.AzureFileEntity(file_name, blob_client)

    @ExceptionHandler.decorated
    def get_file_from_url(self, container_name: str, full_url: str):
        path = '/'.join(urllib.parse.unquote(full_url).split('/')[4:])
        file = azure_file_entity.AzureFileEntity
        client_container = self._blob_service_client.get_container_client(container_name)
        blob_client = azure_storage_container.AzureStorageContainer(container_name, client_container)
        files = blob_client.list_files()
        for file_info in files:
            if file_info.file_path == path:
                file = file_info
        return file
