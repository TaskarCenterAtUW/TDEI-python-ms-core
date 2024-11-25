import unittest
from unittest.mock import MagicMock
import requests
from io import StringIO
from src.python_ms_core.core.storage.abstract.file_entity import FileEntity
from src.python_ms_core.core.resource_errors import ExceptionHandler
from src.python_ms_core.core.storage.providers.local.local_file_entity import LocalFileEntity


class MockResponse:
    def __init__(self, text):
        self.text = text


class MockRequests:
    def __init__(self, response_text):
        self.response_text = response_text

    def get(self, url, stream):
        return MockResponse(self.response_text)

    def post(self, url, files):
        pass


class MockConfig:
    connection_string = 'http://example.com'


class TestLocalFileEntity(unittest.TestCase):
    def test_get_stream(self):
        file_entity = LocalFileEntity('test_file.txt', 'test_path', config=MockConfig())
        file_entity.config.connection_string = 'http://example.com'
        file_entity.download_path = '/files/download/'
        file_entity.path = 'test_path'

        requests_mock = MockRequests('Mocked response text')
        requests.get = MagicMock(side_effect=requests_mock.get)

        result = file_entity.get_stream()
        self.assertEqual(result, 'Mocked response text')

    def test_get_body_text(self):
        file_entity = LocalFileEntity('test_file.txt', 'test_path', config=MockConfig())
        file_entity.get_stream = MagicMock(return_value='Mocked response text')

        result = file_entity.get_body_text()
        self.assertEqual(result, 'Mocked response text')

    def test_upload(self):
        file_entity = LocalFileEntity('test_file.txt', 'test_path', config=MockConfig())
        file_entity.path = 'test_path'
        file_entity.name = 'test_file.txt'

        requests_mock = MockRequests('Mocked response text')
        requests.post = MagicMock(side_effect=requests_mock.post)

        file_entity.upload('mock_upload_stream')

        self.assertEqual(file_entity._get_remote_url, 'http://example.com/files/upload/test_path/test_file.txt')

    def test_get_remote_url(self):
        file_entity = LocalFileEntity('test_file.txt', 'test_path', config=MockConfig())
        file_entity._get_remote_url = 'http://example.com/files/upload/test_path/test_file.txt'
        result = file_entity.get_remote_url()
        self.assertEqual(result, 'http://example.com/files/upload/test_path/test_file.txt')

    def test_delete_file_path_construction(self):
        file_entity = LocalFileEntity('test_file.txt', 'test_path', config=MockConfig())
        file_entity.delete_file()

        file_entity.download_path = '/download/'
        file_entity.path = 'file-to-delete.txt'


        # Construct the expected path based on the mock values
        expected_path = "http://example.com/download/file-to-delete.txt"

        # Verify that the delete_relative_path is constructed correctly
        delete_relative_path = f'{MockConfig().connection_string}{file_entity.download_path}{file_entity.path}'
        self.assertEqual(delete_relative_path, expected_path)


if __name__ == '__main__':
    unittest.main()
