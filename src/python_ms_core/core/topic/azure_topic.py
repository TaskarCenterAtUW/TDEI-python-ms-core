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
from azure.servicebus.exceptions import ServiceBusError
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
        self.max_renewal_duration = 86400 # Renew the message upto 1 day
        self.lock_renewal = AutoLockRenewer(max_workers=1,on_lock_renew_failure=self.on_renew_error,max_lock_renewal_duration=self.max_renewal_duration)
        self.wait_time_for_message = 5
        self.thread_lock = threading.Lock()
        _log = logging.getLogger('azure.servicebus.auto_lock_renewer')
        _log.setLevel(logging.DEBUG)
        self.internal_message_dict = {}
    
    
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
                            logger.info(f'Received message: {message}')
                            logger.info(f'Delivery count {message.delivery_count}')
                            logger.info(f'Message ID {message.message_id}')

                            existing_message = self.internal_message_dict.get(message.message_id, None)
                            if existing_message is None:
                                self.lock_renewal.register(self.receiver, message, max_lock_renewal_duration=self.max_renewal_duration, on_lock_renew_failure=self.on_renew_error)
                                execution_task = self.executor.submit(self.internal_callback, message, callback)
                                execution_task.add_done_callback(lambda x: self.settle_message(x))
                            else:
                                logger.info(f'Message already exists in internal dictionary: {message.message_id}')
                                logger.info(f'Locked until {message.locked_until_utc}')
                                # self.lock_renewal.close(existing_message)
                                # self.lock_renewal.register(self.receiver, message, max_lock_renewal_duration=self.max_renewal_duration, on_lock_renew_failure=self.on_renew_error)
                            with self.thread_lock:
                                self.internal_message_dict[message.message_id] = message
                    else:
                        time.sleep(self.wait_time_for_message)
                except Exception as e:
                    logger.error(f'Error in receiving messages: {e}')

    
    def on_renew_error(self, error):
        """
        Callback function invoked when there is an error renewing the message lock.
        Args:
            error (Exception): The exception that occurred during lock renewal.
        """
        logger.error(f'Error in renewing lock: {error}')

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
        logger.info(f'Settle message: {incoming_message.message_id}')
        with self.thread_lock:
            current_message = self.internal_message_dict.pop(incoming_message.message_id, None)
        if current_message is None:
            current_message = incoming_message
            logger.info(f'No message found internally')
        else:
            logger.info(f'Popped message from internal dictionary: {current_message.message_id}')
            logger.info(f'{current_message.locked_until_utc} -- {incoming_message.locked_until_utc}')
            logger.info(f'{current_message.delivery_count} -- {incoming_message.delivery_count}')

        try:
            if is_success:
                self.receiver.complete_message(current_message)
            else:
                print(f'Abandoning message: {current_message}')
                self.receiver.abandon_message(current_message) # send back to the topic
        except ServiceBusError as e:
            logger.error(f'Error in settling message: {e}')
            print(f'Locked until {current_message.locked_until_utc}')
            # if message is MessageLockLostError, then renew the lock and try again.
        except Exception as e:
            logger.error(f'Error in settling message: {e}')
            # if message is MessageLockLostError, then renew the lock and try again.
            
        return  

    