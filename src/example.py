# Testing code

import asyncio
import uuid
import datetime
from io import BytesIO, StringIO
from dotenv import load_dotenv
from main import Core
from core.queue.providers import azure_queue_config
from core.queue.models.queue_message import QueueMessage

load_dotenv()

Core.initialize()
print('Hello')

topic = 'gtfs-flex-upload'
subscription = 'uploadprocessor'
some_other_sub = 'usdufs'

topic_config = azure_queue_config.AzureQueueConfig()

topicObject1 = Core.get_topic(topic)
topicObject2 = Core.get_topic('tipic')

print()

queue_message = QueueMessage.data_from({
    'message': str(uuid.uuid4().hex),
    'data': {'a': 1}
})

event_loop_publish = asyncio.get_event_loop()
event_loop_publish.run_until_complete(topicObject1.publish(data=queue_message))
# event_loop_publish.run_forever()

event_loop_subscribe = asyncio.get_event_loop()
msg = event_loop_subscribe.run_until_complete(topicObject1.subscribe(subscription=subscription))
print(msg)
# event_loop_subscribe.run_forever()

azure_client = Core.get_storage_client()

container = azure_client.get_container('tdei-storage-test')

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
a = test_file.upload(file_like_io.read())
print(a)
print('Uploaded')

