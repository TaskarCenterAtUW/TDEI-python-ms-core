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
    
    def get_container_info(self, file_url:str):
        """
        Retrieves the container name and file path from a file URL.

        Args:
            file_url (str): The URL of the file.

        Returns:
            tuple: A tuple containing the container name and file path.
        """
        container_name = file_url.split('/')[3]
        file_path = '/'.join(file_url.split('/')[4:])
        return container_name, file_path
    

    def clone_file(self, file_url:str, destination_container_name:str, destination_file_path:str):
        """
        Clones a file from one container to another.

        Args:
            file_url (str): The URL of the file to clone.
            destination_container_name (str): The name of the destination container.
            destination_file_path (str): The path of the destination file.
        """
        source_container_name, source_file_path = self.get_container_info(file_url)
        source_container = self._blob_service_client.get_container_client(source_container_name)
        source_blob = source_container.get_blob_client(source_file_path)
        destination_container = self._blob_service_client.get_container_client(destination_container_name)
        destination_blob = destination_container.get_blob_client(destination_file_path)
        destination_blob.start_copy_from_url(source_blob.url)
        return destination_blob