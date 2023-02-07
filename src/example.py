# Testing code

import uuid
import datetime
from io import BytesIO, StringIO

from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage

core = Core()
print('Hello')

topic = 'gtfs-flex-upload'
subscription = 'upload-validation-processor-test'
some_other_sub = 'usdufs'


def publish_messages(topic_name):
    topic_object = core.get_topic(topic_name=topic_name)
    queue_message = QueueMessage.data_from({
        'message': str(uuid.uuid4().hex),
        'data': {'a': 1}
    })
    topic_object.publish(data=queue_message)


def subscribe(topic_name, subscription_name):
    def process(message):
        print(message)

    topic_object = core.get_topic(topic_name=topic_name)
    try:
        topic_object.subscribe(subscription=subscription_name, callback=process)
    except Exception as e:
        print(e)


publish_messages(topic)
subscribe(topic, subscription)

azure_client = core.get_storage_client()

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
try:
    test_file = container.create_file(f'{filename}.txt')
except Exception as e:
    print(e)
print('Start uploading...')
test_file.upload(file_like_io.read())
print(test_file.get_remote_url())
print('Uploaded Successfully')

logger = core.get_logger()
logger.record_metric(name='test', value='test')

# logger = core.get_logger()
# logger.record_metric(name='test', value='test')
