import os
from dotenv import load_dotenv
from .azure_queue_config import AzureQueueConfig
from azure.servicebus import ServiceBusClient, ServiceBusReceiver, ServiceBusSender

load_dotenv()


class AzureServiceBusTopic:
    sb_client = ServiceBusClient
    listener = ServiceBusReceiver
    sender = ServiceBusSender
    topic = ''

    def __init__(self):
        config = AzureQueueConfig()
        self.provider = config.provider
        self.connection_string = os.environ.get('QUEUECONNECTION', '')
