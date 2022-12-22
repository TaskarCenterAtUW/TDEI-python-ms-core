# Core package for microservice


## System requirements
| Software | Version |
|----------|--------|
| Python   | 3.9.16 |


## Starting a new project with template

- Add `python-ms-core` package as dependency in your `requirements.txt`
- Start using the core packages in your code.

# Structure and components



## Core
Contains all the abstract and Azure implementation classes for connecting to Azure components.

## Initialize and Configuration
All the cloud connections are initialized with `initialize` function of core which takes an optional parameter of type `CoreConfig`. A `CoreConfig` takes only one parameter called `provider` which by default is set to `Azure`. The Core.initialize method can be called without any parameter or with a constructed CoreConfig object.

Eg.
```typescript
Core.initialize();
//or
Core.initialize(new CoreConfig());

```
The method analyzes the `.env` variables and does a health check on what components are available

## Setting up local connections
`Core` works with all the default options and wherever required, relies on environment variables for connecting. The environment variables can be accessed either by setting them in the local machine or by importing via `dotenv` package which reads from a `.env` file created in the source code. All the variables in the `.env` file are optional. However, some of them will be needed inorder for the specific features to work.

Here is the structure 

```shell
# Provider information. Only two options available Azure and Local
# Defaults to Azure if not provided
PROVIDER=Azure 

# Connection string to queue. 
# Optional. Logger functionality for Azure may not work 
# if not provided
QUEUECONNECTION=
# connection string to Azure storage if the provider is Azure
# Same can be used for root folder in Local provider
STORAGECONNECTION=
# Name of the queue that the logger writes to.
# This is optional and defaults value tdei-ms-log
LOGGERQUEUE=

```
This file will have to be generated or shared offline as per the developer requirement.

### Logger
Offers helper classes to help log the information. It is also used to record the audit messages
as well as the analytics information required.

Use `Core.getLogger()` to log the following

`queueMessage`  : Message received or sent to Queues. This helps in keeping track of the messages received and sent from the queue.


Note:

### Model
Offers easy ways to define and parse the model classes from the JSON based input received from either HTTP request or from the queue message. This acts as the base for defining all the models. `AbstractDomainEntity` can be subclassed and used for all the models used within the project. This combined with `Prop()` decorator will make it easy for modelling.

### Queue
Queue component offers easy way to listen to and send messages over Azure Queues/Cloud queues.

All the queue messages have to be derived from the base class `QueueMessage` which has some inherent properties that may be filled (eg. messageType is needed).

### Accessing specific queue
All the interactions will be handled by the class `Queue` which can be initialized with `Core`

### Sending message to queue

Use the `send` method in `Queue` to send the message

```python
import datetime
import asyncio
from main import Core 
from core.queue.models.queue_message import QueueMessage

topic_object = Core.get_topic('TOPIC NAME')
queue_message = QueueMessage.data_from(
    {'messageType': 'sampleevent', 'messageId': '1', 'message': "Sample message", 'publishedDate': datetime.datetime.now()});
event_loop_publish = asyncio.get_event_loop()
event_loop_publish.run_until_complete(topic_object.publish(data=queue_message))
```


```

### Topic
Topic is an advanced version of Queue where the messages are published and subscribed. Each message published to a topic can be subscribed 
by multiple parties for their own analysis and purpose. The messages sent and received via a topic will still be of type `QueueMessage`

The configuration required by Queue and Topic is similar and will be handled via a connection string.

### Accessing a specific topic

Topic can be accessed by the core method `get_topic`. This method takes two parameters 
1. topic name (required)
```python
const topic = Core.get_topic('topicName');
// Alternative
const topic_config = AzureQueueConfig(); // Need to modify this somehow.

topic_config.connectionString = "connectionString";

const topic_object = Core.get_topic(topicConfig,topic);

```

### Publishing message to topic

Once the topic object is got, use `publish` method to publish the message to topic. 
```typescript
topicObject.publish(QueueMessage.from(
    {
        message:"Test message"
    }
));

```

### Subscribing to topic
An active subscription will listening to a subscription over the topic. This is achieved by using `subscribe` method of `Topic`.
It takes two parameters
1. subscription name
2. handler interface object (for when message is received and when there is an error)

```python

event_loop_subscribe = asyncio.get_event_loop()
msg = event_loop_subscribe.run_until_complete(topicObject.subscribe(subscription=subscription))
print(msg)
```

### Storage
For all the azure blobs and other storages, storage components will offer simple ways to upload/download and read the existing data.

There are two ways to fetch the content of the file.
1. ReadStream - use `file.read()` which gives a `BytesIO, StringIO` object 



