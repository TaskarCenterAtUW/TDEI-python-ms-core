# Testing code
import os
import time
import uuid
import random
import threading

from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage

core = Core()
print(f'Core version: {Core.__version__}')
topic = 'temp-request'
subscription = 'temp'
some_other_sub = 'temp'


def publish_messages(topic_name):
    topic_object = core.get_topic(topic_name=topic_name)
    queue_message = QueueMessage.data_from({
        'message': str(uuid.uuid4().hex),
        'data': {'a': random.randint(60, 120)}
    })
    topic_object.publish(data=queue_message)
    print('Message Published')

def long_running_task(sleep_time):
    # Simulate a long-running task
    time.sleep(sleep_time)


def subscribe(topic_name, subscription_name):
    def process(message):
        print(f'Message Received: {message.data}')
        long_running_thread = threading.Thread(target=long_running_task, args=(message.data['a'],))
        long_running_thread.start()
        long_running_thread.join()
        print(f' > Message Completed: {message.data}')

    topic_object = core.get_topic(topic_name=topic_name)
    try:
        topic_object.subscribe(subscription=subscription_name, callback=process)
    except Exception as e:
        print(e)


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
