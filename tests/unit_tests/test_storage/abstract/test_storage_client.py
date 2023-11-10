import unittest
from abc import ABC, abstractmethod


class StorageClient(ABC):
    @abstractmethod
    def get_container(self, name: str):
        pass

    @abstractmethod
    def get_file(self, container_name: str, file_name: str):
        pass

    @abstractmethod
    def get_file_from_url(self, container_name: str, full_url: str):
        pass


class MockStorageClient(StorageClient):
    def __init__(self):
        pass

    def get_container(self, name: str):
        # Mock implementation for getting a container
        return f'Container: {name}'

    def get_file(self, container_name: str, file_name: str):
        # Mock implementation for getting a file
        return f'File: {file_name} from Container: {container_name}'

    def get_file_from_url(self, container_name: str, full_url: str):
        # Mock implementation for getting a file from a URL
        return f'File from URL: {full_url} in Container: {container_name}'


class TestStorageClient(unittest.TestCase):
    def test_get_container(self):
        # Test case for getting a container
        storage_client = MockStorageClient()
        container = storage_client.get_container('test_container')
        self.assertEqual(container, 'Container: test_container')

    def test_get_file(self):
        # Test case for getting a file
        storage_client = MockStorageClient()
        file = storage_client.get_file('test_container', 'test_file.txt')
        self.assertEqual(file, 'File: test_file.txt from Container: test_container')

    def test_get_file_from_url(self):
        # Test case for getting a file from a URL
        storage_client = MockStorageClient()
        file = storage_client.get_file_from_url('test_container', 'https://example.com/test_file.txt')
        expected_result = 'File from URL: https://example.com/test_file.txt in Container: test_container'
        self.assertEqual(file, expected_result)


if __name__ == '__main__':
    unittest.main()
