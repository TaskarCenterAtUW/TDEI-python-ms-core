# Core package for microservice


## System requirements
| Software   | Version |
|------------|---------|
| Python     | 3.10.x  |


## Starting a new project with template

- Add `python-ms-core` package as dependency in your `requirements.txt`
- or `pip install python-ms-core`
- Start using the core packages in your code.



## Core
Contains all the abstract and Azure implementation classes for connecting to Azure components.

## Initialize and Configuration
All the cloud connections are initialized with `initialize` function of core which takes an optional parameter of type `CoreConfig`. A `CoreConfig` takes only one parameter called `provider` which by default is set to `Azure`. The Core.initialize method can be called without any parameter or with a constructed CoreConfig object.

Eg.
```python
from python_ms_core import Core
core = Core() or Core(config='Local')
```
The method analyzes the `.env` variables and does a health check on what components are available

## Setting up local connections
`Core` works with all the default options and wherever required, relies on environment variables for connecting. The environment variables can be accessed either by setting them in the local machine or by importing via `python-dotenv` package which reads from a `.env` file created in the source code. All the variables in the `.env` file are optional. However, some of them will be needed inorder for the specific features to work.

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

Use `core.get_logger()`
Eg.
```python
from python_ms_core import Core

core = Core()
logger = core.get_logger()

# Record a metric
logger.record_metric(name='test', value='test') # Metric and value

```
Note:

* All the `debug`, `info`, `warn`, `error` logs can be logged with `console` and will be injected into appInsight traces.
Eg.
```python
from python_ms_core import Core

core = Core()
logger = core.get_logger()

# Record a metric
logger.debug('Debug Message')
logger.info('Info Message')
logger.warn('Warning Message')
logger.error('Error Message')

```



NOTE: In future, there will be other decorators in place based on the need.
Eg. @Validate, @UUID, @Required

These will help in easily modelling the classes along with the required validation.


### Topic
Topic is an advanced version of Queue where the messages are published and subscribed. Each message published to a topic can be subscribed 
by multiple parties for their own analysis and purpose. The messages sent and received via a topic will still be of type `QueueMessage`

The configuration required by Queue and Topic is similar and will be handled via a connection string.

### Accessing a specific topic

Topic can be accessed by the core method `get_topic`. This method takes two parameters
1. topic name (required)

```python
from python_ms_core import Core

core = Core()
topic = core.get_topic(topic_name='topicName')

```

### Publishing message to topic

Once the topic object is got, use `publish` method to publish the message to topic. 
```python
from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage

core = Core()
topic = core.get_topic(topic_name='topicName')
topic.publish(QueueMessage.data_from(
    {
        'message': 'Test message'
    }
))

```

### Subscribing to topic
An active subscription will listening to a subscription over the topic. This is achieved by using `subscribe` method of `Topic`.
It takes one parameter
1. subscription name


```python
from python_ms_core import Core

core = Core()
topic_object = topic = Core.get_topic(topic_name='topicName')

def process(message):
    print(f'Message Received: {message}')

try:
    topic_object.subscribe(subscription='subscriptionName')
except Exception as e:
    print(e)
```

### Storage
For all the azure blobs and other storages, storage components will offer simple ways to upload/download and read the existing data.
```python
from python_ms_core import Core

core = Core()
# Create storage client
azure_client = core.get_storage_client()

# Get a container in the storage client
container = azure_client.get_container(container_name='tdei-storage-test')

# To get the list of files
list_of_files = container.list_files()

```
There are two ways to fetch the content of the file.
1. ReadStream - use `file.get_stream()` which gives a `stream` object 
2. GetText - use `file.get_body_text()` which gives a `string` object containing all the data of the file in `utf-8` format.

File upload is done only through read stream.
```python
from python_ms_core import Core
from io import BytesIO, StringIO

core = Core()
azure_client = core.get_storage_client()
container = azure_client.get_container(container_name='tdei-storage-test')
# Create an instance of `AzureFileEntity` with name and mime-type
txt = 'foo\nbar\nbaz'
file_like_io = StringIO(txt)

test_file = container.create_file('text.txt', 'text/plain')
# Call the upload method with the readstream.
test_file.upload(file_like_io.read())
```

## Authorization

Core offers a simple way of verifying the authorization of a user and their role.

Checking the permission involves three steps
1. Preparing a permission request object
2. Getting an authorizer object from core
3. Requesting if the permission is valid/true

### Preparing the permission request

```python
from python_ms_core.core.auth.models.permission_request import PermissionRequest

permission_request = PermissionRequest(
    user_id='<userID>',
    org_id='<orgID>',
    should_satisfy_all=False,
    permissions=['permission1', 'permission2']
)

```

In the above example, `should_satisfy_all` helps in figuring out if all the permissions are needed or any one of the permission is sufficient.

### Getting the authorizer from core

Core exposes `get_authorizer` method with 2 parameters

1. `request_params` parameter which is instance of `PermissionRequest` class (Mandatory Parameter).
2. `config` parameter (Optional)

There are two types of `Authorizer` objects in core. 
1. HostedAuthorizer: checks the permissions against a hosted API
2. SimulatedAuthorizer: makes a simulated authorizer used for local/non-hosted environment.

The following code demonstrates getting the simulated and hosted authorizer
```python
from python_ms_core import Core
core = Core()
# HostedAuthorizer 

hosted_authorizer = core.get_authorizer(config={'provider': 'Hosted', 'api_url': '<AUTH_API_URL>'})

simulated_authorizer = core.get_authorizer(config={'provider': 'Simulated'})

```
In case `api_url` is not provided for `Hosted` auth provider, the core will pick it up from environment variable `AUTHURL`

#### Requesting if certain permission is valid:

Use the method `has_ermission(request_params)` to know if the permission request is valid/not.

```python

# Complete Example
from python_ms_core import Core
from python_ms_core.core.auth.models.permission_request import PermissionRequest

core = Core()


permission_request = PermissionRequest(
    user_id='<userID>',
    org_id='<orgID>',
    should_satisfy_all=False,
    permissions=['permission1', 'permission2']
)

# With Hosted provider
auth_provider = core.get_authorizer(config={'provider': 'Hosted', 'api_url': '<AUTH_API_URL>'})
response = auth_provider.has_permission(request_params=permission_request)
# Response will be boolean

# With Simulated provider
auth_provider = core.get_authorizer(config={'provider': 'Simulated'})
response = auth_provider.has_permission(request_params=permission_request)
# Response will be boolean
```

#### How does Simulated authentication work?
With simulated authentication, the method `has_permission` simply returns the value given in `should_satisfy_all` property in the permission request.
