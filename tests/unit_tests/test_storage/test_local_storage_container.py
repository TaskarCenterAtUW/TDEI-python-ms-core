import unittest
from unittest.mock import MagicMock
import requests
from src.python_ms_core.core.storage.providers.local.local_file_entity import LocalFileEntity
from src.python_ms_core.core.resource_errors import ExceptionHandler
from src.python_ms_core.core.storage.providers.local.local_storage_container import LocalStorageContainer


class MockFileEntity(LocalFileEntity):
    def __init__(self, name, path, config=None):
        super().__init__(name, path, config=config)


class LocalStorageContainerTests(unittest.TestCase):
    def setUp(self):
        self.name = 'test_container'
        self.config = MagicMock()
        self.container = LocalStorageContainer(self.name, self.config)

    def test_list_files(self):
        # Mock the response from the requests.get method
        requests_get_mock = MagicMock(return_value=MagicMock(json=MagicMock(return_value=[
            {'name': 'file1', 'path': f'{self.name}/file1'},
            {'name': 'file2', 'path': f'{self.name}/file2'}
        ])))
        requests.get = requests_get_mock

        # Call the list_files method
        result = self.container.list_files()

        # Assert the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, 'uploadFile')
        self.assertEqual(result[0].path, f'{self.name}/file1')
        self.assertEqual(result[1].name, 'uploadFile')
        self.assertEqual(result[1].path, f'{self.name}/file2')

    def test_create_file(self):
        name = 'test_file.txt'

        # Call the create_file method
        result = self.container.create_file(name)

        # Assert the result
        self.assertIsInstance(result, LocalFileEntity)
        self.assertEqual(result.name, name)
        self.assertEqual(result.path, self.name)


if __name__ == '__main__':
    unittest.main()
