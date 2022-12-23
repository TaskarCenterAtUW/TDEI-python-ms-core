import json
from .providers import azure_service_bus_topic
from ..resource_errors import ExceptionHandler
from .models.queue_message import QueueMessage


class Topic:
    def __init__(self, config, topic_name):
        self.topic = topic_name
        if config.provider == 'Azure':
            try:
                self.azure = azure_service_bus_topic.AzureServiceBusTopic(topic_name)
            except Exception as e:
                print(f'Failed to initialize queue with error: {e}')
        else:
            print('Failed to initialize queue')

    @ExceptionHandler.decorated
    async def subscribe(self, subscription=None):
        messages = []
        async with self.azure.client:
            receiver = self.azure.client.get_subscription_receiver(
                topic_name=self.azure.topic,
                subscription_name=subscription,
            )
            async with receiver:
                received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
                for message in received_msgs:
                    queue_message = QueueMessage.data_from(str(message))
                    messages.append(queue_message)
                    await receiver.complete_message(message)

        return messages

    @ExceptionHandler.decorated
    async def publish(self, data=None):
        message = QueueMessage.to_dict(data)
        async with self.azure.client:
            sender = self.azure.client.get_topic_sender(topic_name=self.azure.topic, )
            async with sender:
                await sender.send_messages(self.azure.sender(json.dumps(message)))
                print('Message Sent')
