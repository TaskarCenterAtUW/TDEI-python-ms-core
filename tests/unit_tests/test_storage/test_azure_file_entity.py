import unittest
from unittest.mock import MagicMock
from azure.storage.blob import BlobClient
from src.python_ms_core.core.storage.providers.azure.azure_file_entity import AzureFileEntity


class TestAzureFileEntity(unittest.TestCase):
    def setUp(self):
        self.name = 'test_file'
        self.blob_client = MagicMock()

    def test_get_stream(self):
        # Create an instance of the AzureFileEntity
        file_entity = AzureFileEntity(self.name, self.blob_client)

        # Mock the download_blob method
        mock_download_blob = MagicMock()
        mock_download_blob.readall.return_value = b'Test content'
        self.blob_client.download_blob.return_value = mock_download_blob

        # Call the get_stream method
        result = file_entity.get_stream()

        # Assert the result
        self.assertEqual(result, b'Test content')
        self.blob_client.download_blob.assert_called_once()

    def test_get_body_text(self):
        # Create an instance of the AzureFileEntity
        file_entity = AzureFileEntity(self.name, self.blob_client)

        # Mock the download_blob method
        mock_download_blob = MagicMock()
        mock_download_blob.content_as_text.return_value = 'Test content'
        self.blob_client.download_blob.return_value = mock_download_blob

        # Call the get_body_text method
        result = file_entity.get_body_text()

        # Assert the result
        self.assertEqual(result, 'Test content')
        self.blob_client.download_blob.assert_called_once()

    def test_upload(self):
        # Create an instance of the AzureFileEntity
        file_entity = AzureFileEntity(self.name, self.blob_client)

        # Mock the upload_blob method
        mock_upload_blob = MagicMock()
        mock_upload_blob.url = 'http://example.com/file'
        self.blob_client.upload_blob.return_value = mock_upload_blob

        # Call the upload method
        upload_stream = b'Test content'
        file_entity.upload(upload_stream)

        # Assert the result
        self.assertEqual(file_entity._get_remote_url, 'http://example.com/file')
        self.blob_client.upload_blob.assert_called_once_with(file_entity.file_path, upload_stream)

    def test_get_remote_url(self):
        # Create an instance of the AzureFileEntity
        file_entity = AzureFileEntity(self.name, self.blob_client)

        # Set the _get_remote_url attribute
        file_entity._get_remote_url = 'http://example.com/file'

        # Call the get_remote_url method
        result = file_entity.get_remote_url()

        # Assert the result
        self.assertEqual(result, 'http://example.com/file')

    def test_delete_file(self):
        # Create an instance of the AzureFileEntity
        file_entity = AzureFileEntity(self.name, self.blob_client)

        # Mock the delete_blob method of blob_client
        mock_delete_blob = MagicMock()
        self.blob_client.delete_blob = mock_delete_blob

        # Call the delete_file method
        file_entity.delete_file()

        # Assertions
        mock_delete_blob.assert_called_once()
        self.blob_client.delete_blob.assert_called_once()


if __name__ == '__main__':
    unittest.main()
