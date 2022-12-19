# Testing code
import os
from main import Core
from core.queue.providers import azure_queue_config
from dotenv import load_dotenv

load_dotenv()

Core.initialize()
print('Hello')

topic = 'gtfs-flex-upload'
subscription = 'uploadprocessor'
some_other_sub = 'usdufs'

topic_config = azure_queue_config.AzureQueueConfig()

a = Core.get_topic(topic)
print(a)