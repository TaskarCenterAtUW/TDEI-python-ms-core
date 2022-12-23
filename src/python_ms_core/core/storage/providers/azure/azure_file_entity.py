from azure.storage.blob import BlobClient
from ...abstract import file_entity


class AzureFileEntity(file_entity.FileEntity):
    blob_client = BlobClient

    def __init__(self, name, mimetype, blob_client):
        super().__init__(name, mimetype)
        self.blob_client = blob_client

    def get_stream(self):
        return self.blob_client.download_blob(encoding='latin1').readall()

    def get_body_text(self):
        return self.blob_client.download_blob().content_as_text()

    def upload(self, upload_stream):
        self.blob_client.upload_blob(self.file_path, upload_stream)
