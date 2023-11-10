import unittest
from abc import ABC, abstractmethod


class StorageContainer(ABC):
    @abstractmethod
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def list_files(self):
        pass

    @abstractmethod
    def create_file(self, name, mimetype):
        pass


class MockStorageContainer(StorageContainer):
    def __init__(self, name):
        super().__init__(name)

    def list_files(self):
        # Mock implementation for listing files
        return ['file1.txt', 'file2.txt', 'file3.txt']

    def create_file(self, name, mimetype):
        # Mock implementation for creating a file
        return f'Created file: {name} ({mimetype})'


class TestStorageContainer(unittest.TestCase):
    def test_init(self):
        # Test case for initializing StorageContainer
        name = 'test_container'
        container = MockStorageContainer(name)
        self.assertEqual(container.name, name)

    def test_list_files(self):
        # Test case for listing files in StorageContainer
        container = MockStorageContainer('test_container')
        files = container.list_files()
        expected_files = ['file1.txt', 'file2.txt', 'file3.txt']
        self.assertListEqual(files, expected_files)

    def test_create_file(self):
        # Test case for creating a file in StorageContainer
        container = MockStorageContainer('test_container')
        file_name = 'test_file.txt'
        mimetype = 'text/plain'
        result = container.create_file(file_name, mimetype)
        expected_result = f'Created file: {file_name} ({mimetype})'
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
