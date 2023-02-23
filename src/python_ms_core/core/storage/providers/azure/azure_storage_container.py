from azure.storage.blob import ContainerClient
from ...abstract import storage_container
from ...providers.azure import azure_file_entity
from ....resource_errors import ExceptionHandler


class AzureStorageContainer(storage_container.StorageContainer):
    container_client = ContainerClient

    def __init__(self, name: str, container_client: ContainerClient):
        super().__init__(name)
        self.container_client = container_client

    @ExceptionHandler.decorated
    def list_files(self, name_starts_with=None):
        if name_starts_with:
            blob_iterator = self.container_client.list_blobs(name_starts_with=name_starts_with)
        else:
            blob_iterator = self.container_client.list_blobs()
        files_list = []
        for single_item in blob_iterator:
            blob_client = self.container_client.get_blob_client(single_item.name)
            files_list.append(azure_file_entity.AzureFileEntity(single_item.name, blob_client=blob_client))
        return files_list

    @ExceptionHandler.decorated
    def create_file(self, name: str):
        return azure_file_entity.AzureFileEntity(name, self.container_client)
