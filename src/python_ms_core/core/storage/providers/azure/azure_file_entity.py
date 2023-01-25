from azure.storage.blob import BlobClient
from ...abstract import file_entity


class AzureFileEntity(file_entity.FileEntity):
    blob_client = BlobClient

    def __init__(self, name, blob_client):
        super().__init__(name)
        self.blob_client = blob_client
        self._get_remote_url = None

    def get_stream(self):
        return self.blob_client.download_blob().readall()

    def get_body_text(self):
        return self.blob_client.download_blob().content_as_text()

    def upload(self, upload_stream):
        upload_file = self.blob_client.upload_blob(self.file_path, upload_stream)
        self._get_remote_url = upload_file.url

    def get_remote_url(self):
        return self._get_remote_url
