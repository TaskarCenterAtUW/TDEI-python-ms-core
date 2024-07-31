import json
import logging
import threading
import time
from .config.topic_config import Config
from .abstract.topic_abstract import TopicAbstract
from ..resource_errors import ExceptionHandler
from ..queue.models.queue_message import QueueMessage

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('Topic')
logger.setLevel(logging.INFO)


class Callback:
    def __init__(self, fn=None, max_concurrent_messages=1):
        self._function_to_call = fn
        self._max_concurrent_messages = max_concurrent_messages
        self._stop_event = threading.Event()
        self._renewal_interval = 10  # seconds

    def _renew_message_lock(self, message, receiver):
        while not self._stop_event.is_set():
            try:
                time.sleep(self._renewal_interval)
                if not message._lock_expired:
                    receiver.renew_message_lock(message)
            except Exception as e:
                break

    # old method to fetch messages. Not used anymore
    def messages(self, provider, topic, subscription):
        with provider.client:
            topic_receiver = provider.client.get_subscription_receiver(topic, subscription_name=subscription)
            logger.info(f'Started receiver for {subscription}')
            with topic_receiver:
                for message in topic_receiver:
                    try:
                        queue_message = QueueMessage.data_from(str(message))
                        self._function_to_call(queue_message)
                    except Exception as e:
                        print(f'Error: {e}, Invalid message received: {message}')
                    finally:
                        topic_receiver.complete_message(message)
            logger.info('Completed topic receiver')
    
    # Sends data to the callback function
    def process_message(self, message, receiver):
        queue_message = QueueMessage.data_from(str(message))
        self._function_to_call(queue_message)
        receiver.complete_message(message)

    # Starts listening to the messages
    def start_listening(self, provider, topic, subscription):
        with provider.client:  # service bus client
            logger.info('Initiating receiver')
            topic_receiver = provider.client.get_subscription_receiver(
                topic_name=topic,
                subscription_name=subscription
            )
            logger.info('Receiver started')
            with topic_receiver:
                while True:
                    try:
                        messages = topic_receiver.receive_messages(
                            max_message_count=self._max_concurrent_messages,
                            max_wait_time=5
                        )
                        if not messages:
                            continue

                        for message in messages:
                            stop_event = threading.Event()
                            lock_renewal_thread = threading.Thread(
                                target=self._renew_message_lock,
                                args=(message, topic_receiver)
                            )
                            lock_renewal_thread.start()
                            try:
                                self.process_message(message, topic_receiver)
                            except Exception as e:
                                logger.error(f'Error processing message: {message}. Error: {e}')
                                topic_receiver.abandon_message(message)
                                logger.info(f'Message {message.message_id} abandoned')
                            finally:
                                stop_event.set()  # Signal the lock renewal thread to stop
                                lock_renewal_thread.join()
                    except Exception as et:
                        logger.error(f'Error in service bus connection: {et}')
                        # Change mode from PEEK_LOCK to RECEIVE_AND_DELETE
                logger.info('Receiver stopped')


class Topic(TopicAbstract):
    def __init__(self, config=None, topic_name=None, max_concurrent_messages=1):
        self.topic = topic_name
        self.provider = Config(config=config, topic_name=topic_name)
        self.max_concurrent_messages = max_concurrent_messages

    @ExceptionHandler.decorated
    def subscribe(self, subscription=None, callback=None):
        if subscription is not None:
            cb = Callback(callback, max_concurrent_messages=self.max_concurrent_messages)
            thread = threading.Thread(target=cb.start_listening, args=(self.provider, self.topic, subscription))
            thread.start()
            time.sleep(5)
        else:
            logging.error(
                f'Unimplemented initialize for core {self.provider.provider}, Subscription name is required!')

    @ExceptionHandler.decorated
    def publish(self, data=None):
        message = QueueMessage.to_dict(data)
        with self.provider.client:
            sender = self.provider.client.get_topic_sender(topic_name=self.provider.topic)
            with sender:
                sender.send_messages(self.provider.sender(json.dumps(message)))
