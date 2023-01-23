import json
import logging
import threading
import time
from .providers.azure_service_bus_topic import AzureServiceBusTopic
from ..resource_errors import ExceptionHandler
from .models.queue_message import QueueMessage


class Callback:
    def __init__(self, fn=None):
        self._function_to_call = fn

    def messages(self, client):
        for message in client:
            try:
                queue_message = QueueMessage.data_from(str(message))
                self._function_to_call(queue_message)
            except Exception as e:
                print(f'Error: {e}, Invalid message received: {message}')
            finally:
                client.complete_message(message)


class Topic:
    def __init__(self, config=None, topic_name=None):
        self.topic = topic_name
        if config.provider == 'Azure':
            try:
                self.provider = AzureServiceBusTopic(topic_name=topic_name)
            except Exception as e:
                logging.error(f'Failed to initialize Topic with error: {e}')
        else:
            logging.error('Failed to initialize Topic')

    @ExceptionHandler.decorated
    def subscribe(self, subscription=None, callback=None):
        if subscription is not None:
            cb = Callback(callback)
            with self.provider.client:
                topic_receiver = self.provider.client.get_subscription_receiver(self.provider.topic,
                                                                                subscription_name=subscription)
                with topic_receiver:
                    if callback and callable(callback):
                        thread = threading.Thread(target=cb.messages, args=(topic_receiver,))
                        thread.start()
                        time.sleep(5)
        else:
            logging.error(
                f'Unimplemented initialization for core {self.provider.provider}, Subscription name is required!')

    @ExceptionHandler.decorated
    def publish(self, data=None):
        message = QueueMessage.to_dict(data)
        with self.provider.client:
            sender = self.provider.client.get_topic_sender(topic_name=self.provider.topic)
            with sender:
                sender.send_messages(self.provider.sender(json.dumps(message)))
        print('Message Sent')
