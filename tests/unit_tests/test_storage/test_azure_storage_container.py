import unittest
from unittest.mock import MagicMock, patch
from azure.storage.blob import ContainerClient
from src.python_ms_core.core.storage.abstract.storage_container import StorageContainer
from src.python_ms_core.core.storage.providers.azure.azure_file_entity import AzureFileEntity
from src.python_ms_core.core.storage.providers.azure.azure_storage_container import AzureStorageContainer


class TestAzureStorageContainer(unittest.TestCase):
    def setUp(self):
        self.container_name = 'test_container'
        self.container_client = MagicMock(ContainerClient)
        self.storage_container = AzureStorageContainer(self.container_name, self.container_client)

    @patch('src.python_ms_core.core.storage.providers.azure.azure_file_entity.AzureFileEntity')
    def test_list_files(self, mock_file_entity):
        # Mock the behavior of the ContainerClient and BlobClient
        mock_blob_iterator = MagicMock()
        self.container_client.list_blobs.return_value = mock_blob_iterator

        # Create mock blob instances with desired names
        mock_blob1 = MagicMock(name='blob1')
        mock_blob1.name = 'file1'
        mock_blob2 = MagicMock(name='blob2')
        mock_blob2.name = 'file2'

        # Configure the behavior of the mock_blob_iterator to return the mock blobs
        mock_blob_iterator.__iter__.return_value = [mock_blob1, mock_blob2]

        # Configure the behavior of the mock AzureFileEntity
        mock_file_entity_instance = mock_file_entity.return_value
        mock_file_entity.return_value = mock_file_entity_instance

        # Call the method under test
        result = self.storage_container.list_files()

        # Perform assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], mock_file_entity_instance)
        self.assertEqual(result[1], mock_file_entity_instance)
        self.container_client.list_blobs.assert_called_once_with()
        self.container_client.get_blob_client.assert_called()

    @patch('src.python_ms_core.core.storage.providers.azure.azure_file_entity.AzureFileEntity')
    def test_list_files_with_name_starts_with(self, mock_file_entity):
        # Mock the behavior of the ContainerClient and BlobClient
        mock_blob_iterator = MagicMock()
        self.container_client.list_blobs.return_value = mock_blob_iterator
        mock_blob_iterator.__iter__.return_value = [
            MagicMock(name='blob1', return_value='file1'),
            MagicMock(name='blob2', return_value='file2')
        ]
        mock_blob_client = MagicMock()
        self.container_client.get_blob_client.return_value = mock_blob_client

        # Configure the behavior of the mock AzureFileEntity
        mock_file_entity_instance = mock_file_entity.return_value
        mock_file_entity.return_value = mock_file_entity_instance

        # Call the method under test
        result = self.storage_container.list_files(name_starts_with='prefix')

        # Perform assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], mock_file_entity_instance)
        self.assertEqual(result[1], mock_file_entity_instance)
        self.container_client.list_blobs.assert_called_once_with(name_starts_with='prefix')
        self.container_client.get_blob_client.assert_called()

    @patch('src.python_ms_core.core.storage.providers.azure.azure_file_entity.AzureFileEntity')
    def test_create_file(self, mock_file_entity):
        # Configure the behavior of the mock AzureFileEntity
        mock_file_entity_instance = mock_file_entity.return_value
        mock_file_entity.return_value = mock_file_entity_instance

        # Call the method under test
        result = self.storage_container.create_file('file1')

        # Perform assertions
        self.assertEqual(result, mock_file_entity_instance)
        mock_file_entity.assert_called_once_with('file1', self.container_client)


if __name__ == '__main__':
    unittest.main()