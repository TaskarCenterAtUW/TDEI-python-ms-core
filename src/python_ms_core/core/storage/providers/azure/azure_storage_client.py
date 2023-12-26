import logging
import urllib.parse
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from . import azure_file_entity, azure_storage_container
from ...abstract import storage_client
from ....resource_errors import ExceptionHandler
from datetime import datetime, timedelta



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

    @ExceptionHandler.decorated
    def get_downloadable_url(self, full_url: str):
        # Get the path from the url
        unquoted_full_url = urllib.parse.unquote(full_url)
        remote_file_url = urllib.parse.urlparse(unquoted_full_url)
        # Get the container name from the url
        splits = remote_file_url.path.split('/')
        container_name = splits[1] # Gets the container name
        path = '/'.join(urllib.parse.unquote(full_url).split('/')[4:]) # Get the blob name
        sas_token = self._generate_sas_token(container_name=container_name, blobName=path)

        return  full_url+'?'+sas_token
    
    # Internal method to generate SAS token
    # This does not guarantee result if the file is not there 
    # in the path specified

    def _generate_sas_token(self, container_name:str, blobName:str):
        #  Permissions
        permissions = BlobSasPermissions(read=True)
        expiration_time = datetime.utcnow() + timedelta(days=1) # Expiration is 1 day

        sas_token = generate_blob_sas(
            self._blob_service_client.account_name,
            container_name,
            blobName,
            account_key=self._blob_service_client.credential.account_key,
            permission=permissions,
            expiry=expiration_time
        )

        return sas_token