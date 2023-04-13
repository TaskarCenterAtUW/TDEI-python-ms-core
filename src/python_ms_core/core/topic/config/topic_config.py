from azure.servicebus import ServiceBusClient, ServiceBusMessage


class Config:
    def __init__(self, config=None, topic_name=None):
        self.topic = topic_name
        self.provider = config.provider
        self.connection_string = config.connection_string
        if self.provider.lower() == 'azure':
            self.client = ServiceBusClient.from_connection_string(conn_str=self.connection_string, retry_total=10, retry_backoff_factor=1, retry_backoff_max=30)
            self.sender = ServiceBusMessage
