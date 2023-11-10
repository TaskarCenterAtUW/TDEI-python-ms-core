# Testing code
import sys
import os
import time
import uuid
import random
import datetime
from io import BytesIO, StringIO

from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage
from python_ms_core.core.auth.models.permission_request import PermissionRequest

core = Core()
print('Hello')

topic = 'gtfs-pathways-upload'
subscription = 'log'
some_other_sub = 'usdufs'


def publish_messages(topic_name):
    topic_object = core.get_topic(topic_name=topic_name)
    queue_message = QueueMessage.data_from({
        'message': str(uuid.uuid4().hex),
        'data': {'a': random.randint(0, 1000)}
    })
    topic_object.publish(data=queue_message)
    print('Message Published')


def subscribe(topic_name, subscription_name):
    def process(message):
        print(f'Message Received: {message}')
        # Spawn and thread process it -> 1 hr no issues
        # return

    topic_object = core.get_topic(topic_name=topic_name)
    try:
        topic_object.subscribe(subscription=subscription_name, callback=process)
    except Exception as e:
        print(e)


subscribe(topic, subscription)

# azure_client = core.get_storage_client()

# container = azure_client.get_container(container_name='gtfspathways')

# list_of_files = container.list_files()
# if len(list_of_files) > 0:
#     for single in list_of_files:
#         print(single.path)
#     firstFile = list_of_files[0]
#     # print(firstFile.name+'<><>')
#     file_content = firstFile.get_body_text()

# # Creating a text stream
# txt = 'foo\nbar\nbaz'
# file_like_io = StringIO(txt)
# basename = 'sample-file'
# suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
# filename = '_'.join([basename, suffix])
# try:
#     test_file = container.create_file(f'{filename}.txt')
# except Exception as e:
#     print(e)
# print('Start uploading...')
# test_file.upload(file_like_io.read())
# print(test_file.get_remote_url())
# print('Uploaded Successfully')

# logger = core.get_logger()
# logger.record_metric(name='test', value='test')

# publish_messages(topic)
# time.sleep(2)

# permission_params = PermissionRequest(
#     user_id='7961d767-a352-464f-95b6-cd1c5189a93c',
#     project_group__id='5e339544-3b12-40a5-8acd-78c66d1fa981',
#     should_satisfy_all=False,
#     permissions=['poc']
# )

# try:
#     auth = core.get_authorizer()
#     resp = auth.has_permission(request_params=permission_params)
#     print(resp)
# except Exception as e:
#     print(f'Request failed with Code: {e.status_code}, Message: {e.message}')
#     print()

# os._exit(os.EX_OK)
