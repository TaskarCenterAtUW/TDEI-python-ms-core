import unittest
from src.python_ms_core.core.storage.abstract.file_entity import FileEntity


class MockFileEntity(FileEntity):
    def __init__(self, name: str):
        super().__init__(name)

    def get_stream(self):
        # Mock implementation for getting the stream
        return 'Mock Stream'

    def get_body_text(self):
        # Mock implementation for getting the body text
        return 'Mock Body Text'

    def upload(self, upload_stream):
        # Mock implementation for uploading
        return 'Mock Upload'

    def get_remote_url(self):
        # Mock implementation for getting the remote URL
        return 'http://example.com/file.txt'
    def delete_file(self):
        # Mock implementation for deleting the file
        pass


class TestFileEntity(unittest.TestCase):
    def test_init(self):
        # Test case for initializing FileEntity
        name = 'test_file.txt'
        file_entity = MockFileEntity(name)
        self.assertEqual(file_entity.name, name)
        self.assertEqual(file_entity.file_path, name)

    def test_get_stream(self):
        # Test case for getting stream from FileEntity
        file_entity = MockFileEntity('test_file.txt')
        stream = file_entity.get_stream()
        self.assertEqual(stream, 'Mock Stream')

    def test_get_body_text(self):
        # Test case for getting body text from FileEntity
        file_entity = MockFileEntity('test_file.txt')
        body_text = file_entity.get_body_text()
        self.assertEqual(body_text, 'Mock Body Text')

    def test_upload(self):
        # Test case for uploading to FileEntity
        file_entity = MockFileEntity('test_file.txt')
        result = file_entity.upload('Mock Stream')
        self.assertEqual(result, 'Mock Upload')

    def test_get_remote_url(self):
        # Test case for getting the remote URL from FileEntity
        file_entity = MockFileEntity('test_file.txt')
        remote_url = file_entity.get_remote_url()
        self.assertEqual(remote_url, 'http://example.com/file.txt')


if __name__ == '__main__':
    unittest.main()
