import unittest
from unittest.mock import MagicMock
import logging
import urllib.parse
from src.python_ms_core.core.storage.providers.local.local_storage_container import LocalStorageContainer
from src.python_ms_core.core.storage.providers.local.local_file_entity import LocalFileEntity
from src.python_ms_core.core.storage.providers.local.local_storage_client import LocalStorageClient


class MockConfig:
    provider = 'local'


class MockContainer:
    def __init__(self, name):
        self.name = name


class MockFileEntity:
    def __init__(self, name, path, config=None):
        self.name = name
        self.path = path
        self.config = config


class MockStorageContainer:
    def __init__(self, config, name):
        self.config = config
        self.name = name

    def list_files(self):
        return [MockFileEntity('uploadFile', f'{self.name}/file1', config=self.config),
                MockFileEntity('uploadFile', f'{self.name}/file2', config=self.config)]


class TestLocalStorageClient(unittest.TestCase):
    def setUp(self):
        self.config = MockConfig()
        self.client = LocalStorageClient(self.config)

    def test_get_container(self):
        container_name = 'test_container'
        result = self.client.get_container(container_name)
        self.assertIsInstance(result, LocalStorageContainer)
        self.assertEqual(result.name, container_name)

    def test_get_container_without_name(self):
        with self.assertLogs(level=logging.ERROR) as logs:
            result = self.client.get_container(None)
            self.assertIsNone(result)
            self.assertIn('Container name is required!', logs.output[0])

    def test_get_file(self):
        container_name = 'test_container'
        file_name = 'test_file.txt'
        result = self.client.get_file(container_name, file_name)
        self.assertIsInstance(result, LocalFileEntity)
        self.assertEqual(result.name, 'uploadFile')
        self.assertEqual(result.path, f'{container_name}/{file_name}')

    def test_get_file_from_url(self):
        container_name = 'test_container'
        full_url = 'http://example.com/files/upload/test_container/file2'
        LocalStorageContainer.list_files = MagicMock(return_value=[
            MockFileEntity('uploadFile', 'test_container/file1', config=self.config),
            MockFileEntity('uploadFile', 'test_container/file2', config=self.config)
        ])

        result = self.client.get_file_from_url(container_name, full_url)
        self.assertIsInstance(result, MockFileEntity)
        self.assertEqual(result.name, 'uploadFile')
        self.assertEqual(result.path, f'{container_name}/file2')


if __name__ == '__main__':
    unittest.main()
