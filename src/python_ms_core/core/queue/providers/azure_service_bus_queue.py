from azure.servicebus import ServiceBusClient, ServiceBusMessage


class AzureServiceBusQueue:
    queue_name = ''

    def __init__(self, config, queue_name=None):
        self.queue_name = queue_name or config.logger_queue_name
        self.provider = config.provider
        self.connection_string = config.connection_string
        self.client = ServiceBusClient.from_connection_string(conn_str=self.connection_string, logging_enable=True)
        self.sender = ServiceBusMessage
