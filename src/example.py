# Testing code
import os
from main import Core
from core.queue.providers import azure_queue_config
from dotenv import load_dotenv
from core.queue.models.queue_message import QueueMessage
import asyncio

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
    'message': '111',
    'data': {'a': 1}
})

event_loop_publish = asyncio.get_event_loop()
event_loop_publish.run_until_complete(topicObject1.publish(data=queue_message))
# event_loop_publish.run_forever()

event_loop_subscribe = asyncio.get_event_loop()
msg = event_loop_subscribe.run_until_complete(topicObject1.subscribe(subscription=subscription))
print(msg)
event_loop_subscribe.run_forever()

