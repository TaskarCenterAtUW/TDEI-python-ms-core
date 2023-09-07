import logging
import threading
import time
import pika
from .config.topic_config import Config
from .abstract.topic_abstract import TopicAbstract
from ..resource_errors import ExceptionHandler
from ..queue.models.queue_message import QueueMessage


class Callback:
    def __init__(self, fn=None):
        self._function_to_call = fn

    def messages(self, channel, subscription):
        def return_message(ch, method, properties, body):
            self._function_to_call(body)

        channel.basic_consume(queue=subscription, on_message_callback=return_message)
        channel.start_consuming()


class LocalTopic(TopicAbstract):

    def __init__(self, config=None, topic_name=None):
        self.topic = topic_name
        self.config = config
        self.client = Config(config=config, topic_name=topic_name)
        params = pika.URLParameters(self.client.connection_string)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.topic, exchange_type='fanout')

    @ExceptionHandler.decorated
    def subscribe(self, subscription=None, callback=None):

        if subscription is not None:
            if self.connection.is_open:
                self.connection.close()
            self.client = Config(config=self.config, topic_name=self.topic)
            params = pika.URLParameters(self.client.connection_string)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            time.sleep(3)
            self.channel.exchange_declare(exchange=self.topic, exchange_type='fanout')
            self.channel.queue_declare(queue=subscription, exclusive=True)
            self.channel.queue_bind(queue=subscription, exchange=self.topic, routing_key='')
            cb = Callback(callback)
            thread = threading.Thread(target=cb.messages, args=(self.channel, subscription))
            # thread.daemon = True
            thread.start()
        else:
            logging.error(
                f'Unimplemented initialize for core {self.provider.provider}, Subscription name is required!')

    @ExceptionHandler.decorated
    def publish(self, data=None):
        self.channel.basic_publish(exchange=self.topic, routing_key='', body=str(QueueMessage.to_dict(data)))
