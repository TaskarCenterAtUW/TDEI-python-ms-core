import logging
from azure.storage.blob import BlobServiceClient
from ...abstract import storage_client
from . import azure_storage_config, azure_file_entity, azure_storage_container


class AzureStorageClient(storage_client.StorageClient):
    _blob_service_client: BlobServiceClient

    def __init__(self, config: azure_storage_config.AzureStorageConfig):
        super().__init__()
        self._blob_service_client = BlobServiceClient.from_connection_string(config.connection_string)

    def get_container(self, container_name=None):
        if container_name is not None:
            client_container = self._blob_service_client.get_container_client(container_name)
            return azure_storage_container.AzureStorageContainer(container_name, client_container)
        else:
            logging.error(f'Unimplemented initialization for core {self.config.provider}, Container name is required!')
            return

    def get_file(self, container_name, file_name):
        client_container = self._blob_service_client.get_container_client(container_name)
        blob_client = client_container.get_blob_client(file_name)
        properties = blob_client.get_blob_properties()
        return azure_file_entity.AzureFileEntity(file_name, properties.blob_type, blobClient=blob_client)

    def get_file_from_url(self, full_url):
        return super().getFileFromUrl(full_url)
