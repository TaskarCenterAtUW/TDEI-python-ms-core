from dotenv import load_dotenv

from azure.servicebus import ServiceBusClient, ServiceBusMessage
from .azure_queue_config import AzureQueueConfig


class AzureServiceBusTopic:
    topic = ''

    def __init__(self, topic_name=None):
        config = AzureQueueConfig()
        self.topic = topic_name
        self.provider = config.provider
        self.connection_string = config.connection_string
        self.client = ServiceBusClient.from_connection_string(conn_str=self.connection_string)
        self.sender = ServiceBusMessage
