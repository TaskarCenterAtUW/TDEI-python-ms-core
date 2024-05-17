import logging
import urllib.parse
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from . import azure_file_entity, azure_storage_container
from ...abstract import storage_client
from ....resource_errors import ExceptionHandler
import datetime

class AzureStorageClient(storage_client.StorageClient):
    """
    Represents a client for interacting with Azure Storage.
    """

    _blob_service_client: BlobServiceClient

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._blob_service_client = BlobServiceClient.from_connection_string(config.connection_string)

    @ExceptionHandler.decorated
    def get_container(self, container_name: str):
        """
        Retrieves the Azure Storage container with the specified name.

        Args:
            container_name (str): The name of the container.

        Returns:
            azure_storage_container.AzureStorageContainer: The Azure Storage container object.
        """
        if container_name:
            client_container = self._blob_service_client.get_container_client(container_name)
            return azure_storage_container.AzureStorageContainer(container_name, client_container)
        else:
            logging.error(f'Unimplemented initialize for core {self.config.provider}, Container name is required!')
            return

    @ExceptionHandler.decorated
    def get_file(self, container_name: str, file_name: str):
        """
        Retrieves the Azure Storage file with the specified name from the specified container.

        Args:
            container_name (str): The name of the container.
            file_name (str): The name of the file.

        Returns:
            azure_file_entity.AzureFileEntity: The Azure Storage file object.
        """
        client_container = self._blob_service_client.get_container_client(container_name)
        blob_client = client_container.get_blob_client(file_name)
        return azure_file_entity.AzureFileEntity(file_name, blob_client)

    @ExceptionHandler.decorated
    def get_file_from_url(self, container_name: str, full_url: str):
        """
        Retrieves the Azure Storage file from the specified URL.

        Args:
            container_name (str): The name of the container.
            full_url (str): The full URL of the file.

        Returns:
            azure_file_entity.AzureFileEntity: The Azure Storage file object.
        """
        path = '/'.join(urllib.parse.unquote(full_url).split('/')[4:])
        file = azure_file_entity.AzureFileEntity
        client_container = self._blob_service_client.get_container_client(container_name)
        blob_client = azure_storage_container.AzureStorageContainer(container_name, client_container)
        files = blob_client.list_files()
        for file_info in files:
            if file_info.file_path == path:
                file = file_info
        return file


    def get_sas_url(self, container_name: str, file_path: str,  expiry_hours:int = 12) -> str:
            """
            Generates a Shared Access Signature (SAS) URL for the specified Azure Storage file.

            Args:
                container_name (str): The name of the container.
                file_path (str): The path of the file within the container.
                expiry_hours (int, optional): The number of hours until the SAS URL expires. Defaults to 12.

            Returns:
                str: The SAS URL for the file.
            """
            sas_token = generate_blob_sas(
                self._blob_service_client.account_name,
                container_name,
                file_path,
                account_key=self._blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
            )
            sas_url = f"https://{self._blob_service_client.account_name}.blob.core.windows.net/{container_name}/{file_path}?{sas_token}"
            return sas_url
