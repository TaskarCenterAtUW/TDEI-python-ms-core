# Testing code

import uuid
import datetime
from io import BytesIO, StringIO
from dotenv import load_dotenv
from python_ms_core import Core
from python_ms_core.core.queue.providers import azure_queue_config
from python_ms_core.core.queue.models.queue_message import QueueMessage

load_dotenv()

Core.initialize()
print('Hello')

topic = 'gtfs-flex-upload'
subscription = 'uploadprocessor'
some_other_sub = 'usdufs'

topic_config = azure_queue_config.AzureQueueConfig()

topicObject1 = Core.get_topic(topic_name=topic)
topicObject2 = Core.get_topic(topic_name='tipic')

print()

queue_message = QueueMessage.data_from({
    'message': str(uuid.uuid4().hex),
    'data': {'a': 1}
})

topicObject1.publish(data=queue_message)

msg = topicObject1.subscribe(subscription=subscription)
print(f'Received message: {msg}')

azure_client = Core.get_storage_client()

container = azure_client.get_container(container_name='tdei-storage-test')

list_of_files = container.list_files()
for single in list_of_files:
    print(single.name)
firstFile = list_of_files[2]
# print(firstFile.name+'<><>')
file_content = firstFile.get_body_text()

# Creating a text stream
txt = 'foo\nbar\nbaz'
file_like_io = StringIO(txt)
basename = 'sample-file'
suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
filename = '_'.join([basename, suffix])
test_file = container.create_file(f'{filename}.txt', 'text/plain')
print('Start uploading...')
test_file.upload(file_like_io.read())
print('Uploaded Successfully')

logger = Core.get_logger(queue_name='tdei-ms-log')
logger.record_metric(name='test', value='test')

logger = Core.get_logger(provider='Local')
logger.record_metric(name='test', value='test')
