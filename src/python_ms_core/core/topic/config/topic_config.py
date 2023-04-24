from azure.servicebus import ServiceBusClient, ServiceBusMessage
import logging

class Config:
    def __init__(self, config=None, topic_name=None):
        self.topic = topic_name
        self.provider = config.provider
        self.connection_string = config.connection_string
        if self.provider.lower() == 'azure':
            # The logging levels below may need to be changed based on the logging that you want to suppress.
            uamqp_logger = logging.getLogger('uamqp')
            uamqp_logger.setLevel(logging.ERROR)

            # or even further fine-grained control, suppressing the warnings in uamqp.connection module
            uamqp_connection_logger = logging.getLogger('uamqp.connection')
            uamqp_connection_logger.setLevel(logging.ERROR)
            self.client = ServiceBusClient.from_connection_string(conn_str=self.connection_string, retry_total=10, retry_backoff_factor=1, retry_backoff_max=30)
            self.sender = ServiceBusMessage
            # receiver = self.client.get_subscription_receiver('','')
            # receiver.receive_messages(1,50)
            # with receiver:
            #     for message in receiver:
            #         print('')
            # self.client.get_subscription_receiver()
