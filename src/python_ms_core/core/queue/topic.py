import json
import logging
from .providers.azure_service_bus_topic import AzureServiceBusTopic
from ..resource_errors import ExceptionHandler
from .models.queue_message import QueueMessage


class Topic:
    def __init__(self, config=None, topic_name=None, callback=None):
        self.topic = topic_name
        self._callback = callback
        self._messages = []
        if config.provider == 'Azure':
            try:
                self.azure = AzureServiceBusTopic(topic_name=topic_name)
            except Exception as e:
                logging.error(f'Failed to initialize Topic with error: {e}')
        else:
            logging.error('Failed to initialize Topic')

    @ExceptionHandler.decorated
    def subscribe(self, subscription=None):
        if subscription is not None:
            with self.azure.client:
                topic_receiver = self.azure.client.get_subscription_receiver(self.azure.topic, subscription_name=subscription)
                with topic_receiver:
                    for message in topic_receiver:
                        queue_message = QueueMessage.data_from(str(message))
                        self._messages = queue_message
                        if self._callback and callable(self._callback):
                            self._callback(self)
                        topic_receiver.complete_message(message)

        else:
            logging.error(
                f'Unimplemented initialization for core {self.config.provider}, Subscription name is required!')

    def get_messages(self):
        return self._messages

    @ExceptionHandler.decorated
    def publish(self, data=None):
        message = QueueMessage.to_dict(data)
        with self.azure.client:
            sender = self.azure.client.get_topic_sender(topic_name=self.azure.topic)
            with sender:
                sender.send_messages(self.azure.sender(json.dumps(message)))
                print('Message Sent')
