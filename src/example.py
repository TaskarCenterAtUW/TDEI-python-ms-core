# Testing code
import os
import time
import uuid
import random
import datetime
from io import BytesIO, StringIO
import threading

from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage
from python_ms_core.core.auth.models.permission_request import PermissionRequest

core = Core()
print(f'Core version: {Core.__version__}')
topic = 'temp-nar'
subscription = 'temp'
some_other_sub = 'temp'
respond_topic = 'temp-response'
# respond_topic_object = core.get_topic(topic_name=respond_topic)


class MessageSender:
    def __init__(self, topic_name):
        self.topic = core.get_topic(topic_name=topic_name)

    def send_message(self, message):
        self.topic.publish(data=QueueMessage.data_from(message))




def publish_messages(topic_name):
    topic_object = core.get_topic(topic_name=topic_name)
    queue_message = QueueMessage.data_from({
        'message': str(uuid.uuid4().hex),
        'data': {'a': random.randint(10, 25)}
    })
    topic_object.publish(data=queue_message)
    print('Message Published')


def long_running_task(sleep_time):
    # Simulate a long-running task
    time.sleep(sleep_time)
    sender_obj = MessageSender(topic_name=respond_topic)
    sender_obj.send_message({'message': 'Task Completed'})
    print(f' > Task Completed: {sleep_time}')


def subscribe(topic_name, subscription_name):
    def process(message):
        print(f'Message Received: {message.data}')
        # long_running_thread = threading.Thread(target=long_running_task, args=(message.data['a'],))
        # long_running_thread.start()
        # long_running_thread.join()
        long_running_task(message.data['a'])
        print(f' > Message Completed: {message.data}')

    topic_object = core.get_topic(topic_name=topic_name,max_concurrent_messages=2)
    try:
        topic_object.subscribe(subscription=subscription_name, callback=process)
    except Exception as e:
        print(e)



import argparse

parser = argparse.ArgumentParser(description='Process the core topic.')
parser.add_argument('-m','--mode', type=str, help='Mode of operation (publish/subscribe)', required=True)
parser.add_argument('-s','--size', type=int, help='Number of the messages to send', required=False)

mode = parser.parse_args().mode
size = parser.parse_args().size
if mode == 'publish':
    for x in range(size):
        print(f'Publishing message {x+1}')
        publish_messages(topic_name=topic)
if mode == 'subscribe':
    subscribe(topic, subscription)
# subscribe(topic, subscription)
# for x in range(10):
#     publish_messages(topic_name=topic)
    # subscribe(topic, subscription)
# for x in range(10):
#     publish_messages(topic_name=topic)

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
