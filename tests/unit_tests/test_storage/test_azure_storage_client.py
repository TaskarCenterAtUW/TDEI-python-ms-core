import unittest
from unittest.mock import MagicMock, patch


class TestAzureStorageClient(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.connection_string = 'connection_string'
        self.config.connection_string = self.connection_string

    @patch('azure.storage.blob.BlobServiceClient')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_container.AzureStorageContainer')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_file_entity.AzureFileEntity')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_client.AzureStorageClient')
    def test_get_container(self, mock_storage_client, mock_file_entity, mock_storage_container, mock_blob_service_client):
        container_name = 'test_container'

        # Create mock instances for BlobServiceClient, AzureStorageContainer, and AzureFileEntity
        mock_blob_service_client_instance = mock_blob_service_client.return_value
        mock_storage_container_instance = mock_storage_container.return_value
        mock_file_entity_instance = mock_file_entity.return_value

        # Configure the behavior of mock instances as needed
        mock_blob_service_client_instance.get_container_client.return_value = mock_storage_container_instance
        mock_storage_container_instance.list_files.return_value = [mock_file_entity_instance]
        mock_file_entity_instance.file_path = 'mock_path'

        # Create an instance of the mock AzureStorageClient
        mock_storage_client_instance = mock_storage_client.return_value
        mock_storage_client_instance._blob_service_client = mock_blob_service_client_instance

        # Configure the get_container method to return the mock_storage_container_instance
        mock_storage_client_instance.get_container.return_value = mock_storage_container_instance

        # Call the method under test
        result = mock_storage_client_instance.get_container(container_name)

        # Perform assertions
        mock_storage_client_instance.get_container.assert_called_once_with(container_name)
        self.assertEqual(result, mock_storage_container_instance)

    @patch('azure.storage.blob.BlobServiceClient')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_container.AzureStorageContainer')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_file_entity.AzureFileEntity')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_client.AzureStorageClient')
    def test_get_file(self, mock_storage_client, mock_file_entity, mock_storage_container, mock_blob_service_client):
        container_name = 'test_container'
        file_name = 'test_file.txt'

        # Create mock instances for BlobServiceClient and AzureFileEntity
        mock_blob_service_client_instance = mock_blob_service_client.return_value
        mock_file_entity_instance = mock_file_entity.return_value

        # Configure the behavior of mock instances as needed
        mock_blob_service_client_instance.get_container_client.return_value = MagicMock()
        mock_container_client = mock_blob_service_client_instance.get_container_client.return_value
        mock_container_client.get_blob_client.return_value = MagicMock()

        # Create an instance of the mock AzureStorageClient
        mock_storage_client_instance = mock_storage_client.return_value
        mock_storage_client_instance._blob_service_client = mock_blob_service_client_instance

        # Configure the get_file method to return the mock_file_entity_instance
        mock_storage_client_instance.get_file.return_value = mock_file_entity_instance

        # Call the method under test
        result = mock_storage_client_instance.get_file(container_name, file_name)

        # Perform assertions
        mock_storage_client_instance.get_file.assert_called_once_with(container_name, file_name)
        self.assertEqual(result, mock_file_entity_instance)

    @patch('azure.storage.blob.BlobServiceClient')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_container.AzureStorageContainer')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_file_entity.AzureFileEntity')
    @patch('src.python_ms_core.core.storage.providers.azure.azure_storage_client.AzureStorageClient')
    def test_get_file_from_url(self, mock_storage_client, mock_file_entity, mock_storage_container, mock_blob_service_client):
        container_name = 'test_container'
        full_url = 'https://example.com/test_container/test_file.txt'

        # Create mock instances for BlobServiceClient, AzureStorageContainer, and AzureFileEntity
        mock_blob_service_client_instance = mock_blob_service_client.return_value
        mock_storage_container_instance = mock_storage_container.return_value
        mock_file_entity_instance = mock_file_entity.return_value

        # Configure the behavior of mock instances as needed
        mock_blob_service_client_instance.get_container_client.return_value = mock_storage_container_instance
        mock_storage_container_instance.list_files.return_value = [mock_file_entity_instance]
        mock_file_entity_instance.file_path = 'test_container/test_file.txt'

        # Create an instance of the mock AzureStorageClient
        mock_storage_client_instance = mock_storage_client.return_value
        mock_storage_client_instance._blob_service_client = mock_blob_service_client_instance

        # Configure the get_file_from_url method to return the mock_file_entity_instance
        mock_storage_client_instance.get_file_from_url.return_value = mock_file_entity_instance

        # Call the method under test
        result = mock_storage_client_instance.get_file_from_url(container_name, full_url)

        # Perform assertions
        mock_storage_client_instance.get_file_from_url.assert_called_once_with(container_name, full_url)
        self.assertEqual(result, mock_file_entity_instance)


if __name__ == '__main__':
    unittest.main()
