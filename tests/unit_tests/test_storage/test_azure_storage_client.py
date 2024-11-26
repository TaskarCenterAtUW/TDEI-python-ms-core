import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock
from azure.storage.blob import BlobServiceClient, BlobClient, BlobSasPermissions
from src.python_ms_core.core.storage.providers.azure.azure_storage_client import AzureStorageClient
from src.python_ms_core.core.storage.providers.azure.azure_storage_container import AzureStorageContainer
from src.python_ms_core.core.storage.providers.azure.azure_file_entity import AzureFileEntity


class TestAzureStorageClient(unittest.TestCase):

    def setUp(self):
        self.config = MagicMock()
        self.config.connection_string = "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=testkey;EndpointSuffix=core.windows.net"
        self.client = AzureStorageClient(self.config)

    @patch('azure.storage.blob.BlobServiceClient')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_container.AzureStorageContainer')
    def test_get_container(self, mock_storage_container, mock_blob_service_client):
        container_name = 'test_container'

        # Mock the BlobServiceClient and container
        mock_blob_service_client_instance = mock_blob_service_client.return_value
        mock_storage_container_instance = mock_storage_container.return_value
        mock_blob_service_client_instance.get_container_client.return_value = mock_storage_container_instance

        # Call the method under test
        result = self.client.get_container(container_name)

        # Assertions
        self.assertEqual(result, mock_storage_container_instance)

    def test_get_container_without_container_name(self):
        result = self.client.get_container(container_name='')
        self.assertIsNone(result)

    @patch('azure.storage.blob.BlobServiceClient')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_file_entity.AzureFileEntity')
    def test_get_file(self, mock_file_entity, mock_blob_service_client):
        container_name = 'test_container'
        file_name = 'test_file.txt'

        # Mock the BlobServiceClient and AzureFileEntity
        mock_blob_service_client_instance = mock_blob_service_client.return_value
        mock_file_entity_instance = mock_file_entity.return_value

        # Configure the behavior of the mock instances
        mock_blob_service_client_instance.get_container_client.return_value.get_blob_client.return_value = MagicMock()
        mock_blob_service_client_instance.get_container_client.return_value.get_blob_client.return_value = mock_file_entity_instance

        # Call the method under test
        result = self.client.get_file(container_name, file_name)

        # Perform assertions
        self.assertEqual(result, mock_file_entity_instance)

    @patch(
        'src.python_ms_core.core.storage.providers.azure.azure_storage_client.azure_storage_container.AzureStorageContainer')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_client.BlobServiceClient')
    @patch(
        'src.python_ms_core.core.storage.providers.azure.azure_storage_client.azure_file_entity.AzureFileEntity')
    def test_get_file_from_url(self, MockAzureFileEntity, mock_blob_service_client, MockAzureStorageContainer):
        # Arrange
        container_name = 'my-container'
        full_url = 'https://example.blob.core.windows.net/my-container/path/to/file.txt'
        expected_file_path = 'path/to/file.txt'

        # Mocking blob service client and container client
        mock_container_client = MagicMock()
        mock_blob_service_client.get_container_client.return_value = mock_container_client

        # Mock the AzureStorageContainer's list_files method
        mock_blob = MagicMock()
        mock_blob.file_path = expected_file_path
        mock_files = [mock_blob]

        MockAzureStorageContainer.return_value.list_files.return_value = mock_files
        MockAzureFileEntity.return_value = mock_blob

        # Act
        result = self.client.get_file_from_url(container_name, full_url)

        # Assert
        MockAzureStorageContainer.return_value.list_files.assert_called_once()
        self.assertEqual(result, mock_blob)

    @patch(
        'src.python_ms_core.core.storage.providers.azure.azure_storage_client.azure_storage_container.AzureStorageContainer')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_client.BlobServiceClient')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_client.azure_file_entity.AzureFileEntity')
    def test_get_file(self, MockAzureFileEntity, mock_blob_service_client, MockAzureStorageContainer):
        # Arrange
        container_name = 'my-container'
        file_name = 'file.txt'

        # Mocking blob service client and container client
        mock_container_client = MagicMock()
        mock_blob_service_client.get_container_client.return_value = mock_container_client
        mock_blob_client = MagicMock()
        mock_container_client.get_blob_client.return_value = mock_blob_client

        # Mock the AzureFileEntity to return a mock file
        mock_file = MagicMock()
        MockAzureFileEntity.return_value = mock_file

        # Act
        result = self.client.get_file(container_name, file_name)

        # Assert
        self.assertEqual(result, mock_file)

    @patch(
        'src.python_ms_core.core.storage.providers.azure.azure_storage_client.generate_blob_sas')  # Mocking the generate_blob_sas function
    @patch(
        'src.python_ms_core.core.storage.providers.azure.azure_storage_client.BlobServiceClient')  # Mocking BlobServiceClient constructor
    def test_get_sas_url(self, mock_blob_service_client, mock_generate_blob_sas):
        # Define the test inputs
        container_name = 'test_container'
        file_path = 'test_file.txt'
        expiry_hours = 12

        # Mock BlobServiceClient instance and set the account_name and account_key properties
        mock_blob_service_client_instance = MagicMock()
        mock_blob_service_client_instance.account_name = 'testaccount'

        # Mock the credential attribute to simulate the account_key
        # Ensure the correct account_key is set here
        mock_blob_service_client_instance.credential = MagicMock()
        mock_blob_service_client_instance.credential.account_key = 'testaccountkey'

        # Mock the BlobServiceClient constructor to return our mocked instance
        mock_blob_service_client.return_value = mock_blob_service_client_instance

        # Set up mock return value for generate_blob_sas
        mock_generate_blob_sas.return_value = 'sas_token_mock'

        # Call the method under test
        sas_url = self.client.get_sas_url(container_name, file_path, expiry_hours)

        # Expected SAS URL format
        expected_sas_url = f"https://testaccount.blob.core.windows.net/{container_name}/{file_path}?sas_token_mock"

        # Assert that the returned URL matches the expected format
        self.assertEqual(sas_url, expected_sas_url)

    def test_get_container_info_valid_url(self):
        file_url = 'https://example.com/test_container/test_file.txt'

        # Call the method under test
        container_name, file_path = self.client.get_container_info(file_url)

        # Assert the correct container name and file path are returned
        self.assertEqual(container_name, 'test_container')
        self.assertEqual(file_path, 'test_file.txt')


if __name__ == '__main__':
    unittest.main()
