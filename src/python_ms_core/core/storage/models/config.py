import os
from dotenv import load_dotenv

load_dotenv()


class CoreConfig:
    def __init__(self):
        self.provider = os.environ.get('PROVIDER', 'Azure')

    @staticmethod
    def default():
        return CoreConfig()
