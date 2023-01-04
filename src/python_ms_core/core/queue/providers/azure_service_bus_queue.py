from azure.servicebus import ServiceBusClient, ServiceBusMessage


class AzureServiceBusQueue:
    queue_name = ''

    def __init__(self, config):
        self.queue_name = config.logger_queue_name
        self.provider = config.provider
        self.connection_string = config.connection_string
        self.client = ServiceBusClient.from_connection_string(conn_str=self.connection_string, logging_enable=False, retry_total=0)
        self.sender = ServiceBusMessage
