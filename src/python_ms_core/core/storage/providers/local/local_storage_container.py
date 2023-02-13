import requests
from ...abstract.storage_container import StorageContainer
from ...providers.local.local_file_entity import LocalFileEntity
from ....resource_errors import ExceptionHandler


class LocalStorageContainer(StorageContainer):

    def __init__(self, name: str, config):
        super().__init__(name=name)
        self.name = name
        self.config = config
        self.excluded_files = ['.DS_Store']

    @ExceptionHandler.decorated
    def list_files(self):
        files_list = []
        try:
            url = f'{self.config.connection_string}/files/list/{self.name}'
            resp = requests.get(url)
            files = resp.json()
            for file in files:
                try:
                    self.excluded_files.index(file['name'])
                except:
                    files_list.append(LocalFileEntity(file['name'], file['path'], config=self.config))
        except Exception as e:
            print(e)
        return files_list

    @ExceptionHandler.decorated
    def create_file(self, name: str):
        return LocalFileEntity(name, self.name, config=self.config)
