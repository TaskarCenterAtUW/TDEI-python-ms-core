from core.storage.abstract import storage_container
from azure.storage.blob import ContainerClient
from core.storage.providers.azure import azure_file_entity


class AzureStorageContainer(storage_container.StorageContainer):
    container_client = ContainerClient

    def __init__(self, name, container_client: ContainerClient):
        super().__init__(name)
        self.container_client = container_client

    def list_files(self):
        blob_iterator = self.container_client.list_blobs()
        files_fist = [azure_file_entity.AzureFileEntity]
        for single_item in blob_iterator:
            blob_client = self.container_client.get_blob_client(single_item.name)
            files_fist.append(
                azure_file_entity.AzureFileEntity(single_item.name, single_item.content_settings.content_type,
                                                  blob_client=blob_client))
        return files_fist

    def create_file(self, name, mimetype):
        return azure_file_entity.AzureFileEntity(name, mimetype, self.container_client)
