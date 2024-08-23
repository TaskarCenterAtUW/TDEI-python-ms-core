import json

import logging
import time
from ..config.config import TopicConfig
from ..resource_errors import ExceptionHandler
from concurrent.futures import ThreadPoolExecutor
from .abstract.topic_abstract import TopicAbstract
from ..queue.models.queue_message import QueueMessage
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus import AutoLockRenewer
import concurrent.futures as cf
import threading


logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('AzureTopic')
logger.setLevel(logging.INFO)


"""
AzureTopic class represents a topic in Azure Service Bus.
Attributes:
    topic (str): The name of the topic.
    client (ServiceBusClient): The ServiceBusClient object used to interact with the Service Bus.
    max_concurrent_messages (int): The maximum number of concurrent messages to process.
    topic_name (str): The name of the topic.
    publisher (TopicSender): The TopicSender object used to send messages to the topic.
    executor (ThreadPoolExecutor): The ThreadPoolExecutor object used to execute callback functions.
    internal_count (int): The internal count of concurrent messages being processed.
    lock_renewal (AutoLockRenewer): The AutoLockRenewer object used to renew message locks.
    max_renewal_duration (int): The maximum duration in seconds to renew a message lock.
    wait_time_for_message (int): The maximum wait time in seconds to receive messages.
Methods:
    publish(data: QueueMessage) -> None:
        Publishes a message to the topic.
    subscribe(subscription: str, callback) -> None:
        Subscribes to a subscription of the topic and processes incoming messages.
    internal_callback(message, callbackfn) -> ServiceBusMessage:
        Internal callback function that processes a message and invokes the callback function.
    settle_message(x: cf.Future) -> None:
        Sets the message as completed and updates the internal count.
"""
class AzureTopic(TopicAbstract):
    def __init__(self, config: TopicConfig=None, topic_name=None, max_concurrent_messages:int=1):
        self.topic = topic_name
        self.client = ServiceBusClient.from_connection_string(conn_str=config.connection_string, retry_total=10, retry_backoff_factor=1, retry_backoff_max=30)
        self.max_concurrent_messages = max_concurrent_messages
        self.topic_name = topic_name
        self.publisher = self.client.get_topic_sender(topic_name=topic_name)
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_messages)
        self.internal_count = 0
        self.lock_renewal = AutoLockRenewer(max_workers=max_concurrent_messages)
        self.max_renewal_duration = 86400 # Renew the message upto 1 day
        self.wait_time_for_message = 5
        self.thread_lock = threading.Lock()
    
    
    def publish(self, data: QueueMessage):
        """
        Publishes a message to the topic.
        Args:
            data (QueueMessage): The message to publish.
        
        """
        message = QueueMessage.to_dict(data)
        self.publisher.send_messages(ServiceBusMessage(json.dumps(message)))

    def subscribe(self, subscription: str, callback):

        """
        Subscribes to a subscription of the topic and processes incoming messages.
        Args:
            subscription (str): The name of the subscription to subscribe to.
            callback (function): The callback function to invoke for each message.
        """
        self.receiver = self.client.get_subscription_receiver(topic_name=self.topic_name, subscription_name=subscription)
        while True:
                try:
                    to_receive = (self.max_concurrent_messages - self.internal_count)
                    if to_receive > 0:
                        messages = self.receiver.receive_messages(max_message_count=to_receive, max_wait_time=self.wait_time_for_message)
                        if not messages or len(messages) == 0:
                            continue
                        for message in messages: 
                            self.lock_renewal.register(self.receiver, message, max_lock_renewal_duration=self.max_renewal_duration)
                            execution_task = self.executor.submit(self.internal_callback, message, callback)
                            execution_task.add_done_callback(lambda x: self.settle_message(x))
                    else:
                        time.sleep(self.wait_time_for_message)
                except Exception as e:
                    logger.error(f'Error in receiving messages: {e}')

    
    def internal_callback(self, message, callbackfn):
        """
        Internal callback function that processes a message and invokes the callback function.
        Args:
            message (ServiceBusMessage): The message to process.
            callbackfn (function): The callback function to invoke.
        Returns:
            ServiceBusMessage: The processed message.
        """
        try:
            with self.thread_lock:
                self.internal_count += 1 # thread safe.
            queue_message = QueueMessage.data_from(str(message))
            callbackfn(queue_message)
            return [True,message]
        except Exception as e:
            logger.error(f'Error in processing message: {e}')
            return [False,message]
                             
    
    def settle_message(self, x: cf.Future):
        """
        Sets the message as completed and updates the internal count.
        Args:
            x (cf.Future): The future object representing the message processing.
        """
        # Lock the internal count
        with self.thread_lock:
            self.internal_count -= 1
        # Check if the future has an exception
        [is_success,incoming_message] = x.result()
        if is_success:
            self.receiver.complete_message(incoming_message)
        else:
            print(f'Abandoning message: {incoming_message}')
            self.receiver.abandon_message(incoming_message) # send back to the topic
        return  

    