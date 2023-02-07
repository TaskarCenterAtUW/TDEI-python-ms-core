from azure.servicebus import ServiceBusClient, ServiceBusMessage


class Config:
    def __init__(self, config=None):
        self.provider = config.provider
        self.connection_string = config.connection_string
        if self.provider.lower() == 'azure':
            self.client = ServiceBusClient.from_connection_string(conn_str=self.connection_string, retry_total=0)
            self.sender = ServiceBusMessage
