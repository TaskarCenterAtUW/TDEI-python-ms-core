from azure.servicebus import ServiceBusClient, ServiceBusMessage


class Config:
    def __init__(self, config=None):
        self.queue_name = config.queue_name
        self.provider = config.provider
        if self.provider.lower() == 'azure':
            self.connection_string = config.connection_string
            self.client = ServiceBusClient.from_connection_string(conn_str=self.connection_string, logging_enable=False,
                                                                  retry_total=0)
            self.sender = ServiceBusMessage
