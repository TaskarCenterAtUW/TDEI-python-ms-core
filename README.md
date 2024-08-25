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

# To check the package version
Core.__version__ # 0.0.21
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
topic = core.get_topic(topic_name='topicName') # By default, process messages concurrently which are available CPU cores  
topic = core.get_topic(topic_name='topicName', max_concurrent_messages=10) # Process 10 messages concurrently  

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
    topic_object.subscribe(subscription='subscriptionName',process)
except Exception as e:
    print(e)
```

- Please note that `subscribe` is a blocking call which runs on a loop. Either use a `thread.Thread` to subscribe or an async method to continue with the other parts of the program

eg.
```python

from python_ms_core import Core
import threading

core = Core()
topic_object = topic = Core.get_topic(topic_name='topicName')

def process(message):
    print(f'Message Received: {message}')

try:
    thread = threading.Thread(topic_object.subscribe, ['subscriptionName',process])
    thread.start()
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
    project_group_id='<projectGroupID>',
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

Use the method `has_permission(request_params)` to know if the permission request is valid/not.

```python

# Complete Example
from python_ms_core import Core
from python_ms_core.core.auth.models.permission_request import PermissionRequest

core = Core()


permission_request = PermissionRequest(
    user_id='<userID>',
    project_group_id='<projectGroupID>',
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


### Testing

The project is configured with `python` to figure out the coverage of the unit tests. All the tests are in `tests` folder.
- To execute the tests, please follow the commands:

   `pip install -r requirements.txt`

   `python -m unittest discover -v tests/unit_tests`
 
- To execute the code coverage, please follow the commands:

    `coverage run --source=src/python_ms_core -m unittest discover -v tests/unit_tests`
 
    `coverage html` // Can be run after 1st  command
 
    `coverage report` // Can be run after 1st  command

- After the commands are run, you can check the coverage report in `htmlcov/index.html`. Open the file in any browser, and it shows complete coverage details
- The terminal will show the output of coverage like this
```shell

>  python -m coverage run --source=src/python_ms_core -m unittest discover -v tests/unit_tests
test_has_permission (test_auth.abstract.test_authorizer_abstraction.TestAuthorizerAbstract) ... ok
test_get_search_params (test_auth.models.test_permission_request.TestPermissionRequest) ... ok
test_has_permission_with_invalid_permissions (test_auth.provider.test_hosted_authorizer.TestHostedAuthorizer) ... ok
test_has_permission_with_missing_auth_url (test_auth.provider.test_hosted_authorizer.TestHostedAuthorizer) ... ok
test_has_permission_with_valid_permissions (test_auth.provider.test_hosted_authorizer.TestHostedAuthorizer) ... ok
test_has_permission_should_return_should_satisfy_all (test_auth.provider.test_simulated_authorizer.TestSimulatedAuthorizer) ... ok
test_has_permission_should_return_should_satisfy_none (test_auth.provider.test_simulated_authorizer.TestSimulatedAuthorizer) ... ok
test_core_config_auth (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_auth_url (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_auth_url_default (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_logger (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_provider (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_provider_default (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_provider_override (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_queue (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_queue_connection (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_queue_connection_default (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_queue_name (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_queue_name_default (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_storage (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_storage_connection (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_storage_connection_default (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_topic (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_topic_connection (test_config.test_cofig.TestCoreConfig) ... ok
test_core_config_topic_connection_default (test_config.test_cofig.TestCoreConfig) ... ok
test_local_config_auth (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_logger (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_provider (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_provider_default (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_queue (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_queue_connection (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_queue_connection_default (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_queue_name (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_queue_name_default (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_storage (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_storage_connection (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_storage_connection_default (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_topic (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_topic_connection (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_topic_connection_default (test_config.test_cofig.TestLocalConfig) ... ok
test_local_config_auth (test_config.test_cofig.TestUnknownConfig) ... ok
test_unknown_config_logger (test_config.test_cofig.TestUnknownConfig) ... ok
test_unknown_config_provider (test_config.test_cofig.TestUnknownConfig) ... ok
test_unknown_config_queue (test_config.test_cofig.TestUnknownConfig) ... ok
test_unknown_config_queue_connection_default (test_config.test_cofig.TestUnknownConfig) ... ok
test_unknown_config_queue_name_default (test_config.test_cofig.TestUnknownConfig) ... ok
test_unknown_config_storage (test_config.test_cofig.TestUnknownConfig) ... ok
test_unknown_config_storage_connection_default (test_config.test_cofig.TestUnknownConfig) ... ok
test_unknown_config_topic (test_config.test_cofig.TestUnknownConfig) ... ok
test_unknown_config_topic_connection_default (test_config.test_cofig.TestUnknownConfig) ... ok
test_get_authorizer_no_config (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: SIMULATED
ok
test_get_authorizer_with_config_hosted_provider (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: AZURE
ok
test_get_authorizer_with_config_simulated_provider (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: SIMULATED
ok
test_get_authorizer_with_config_unknown_provider (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: UNKNOWN
ok
test_get_logger_azure_provider (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: AZURE
ok
test_get_logger_local_provider (test_core.TestCore) ... ok
test_get_logger_unknown_provider (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: UNKNOWN
ok
test_get_storage_client_azure_provider (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: AZURE
ok
test_get_storage_client_local_provider (test_core.TestCore) ... ok
test_get_storage_client_unknown_provider (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: UNKNOWN
ok
test_get_topic_azure_provider (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: AZURE
ok
test_get_topic_local_provider (test_core.TestCore) ... ok
test_get_topic_unknown_provider (test_core.TestCore) ... 2023-07-03 18:07:41 ERROR    Failed to initialize core.get_logger for provider: UNKNOWN
ok
test_add_request (test_logger.abstract.test_logger_abstract.TestLoggerAbstract) ... ok
test_debug (test_logger.abstract.test_logger_abstract.TestLoggerAbstract) ... ok
test_error (test_logger.abstract.test_logger_abstract.TestLoggerAbstract) ... ok
test_info (test_logger.abstract.test_logger_abstract.TestLoggerAbstract) ... ok
test_record_metric (test_logger.abstract.test_logger_abstract.TestLoggerAbstract) ... ok
test_warn (test_logger.abstract.test_logger_abstract.TestLoggerAbstract) ... ok
test_add_request (test_logger.test_local_logger.TestLocalLogger) ... ok
test_debug (test_logger.test_local_logger.TestLocalLogger) ... ok
test_error (test_logger.test_local_logger.TestLocalLogger) ... ok
test_info (test_logger.test_local_logger.TestLocalLogger) ... ok
test_record_metric (test_logger.test_local_logger.TestLocalLogger) ... ok
test_warn (test_logger.test_local_logger.TestLocalLogger) ... ok
test_add_request (test_logger.test_logger.TestLogger) ... ok
test_debug (test_logger.test_logger.TestLogger) ... ok
test_error (test_logger.test_logger.TestLogger) ... ok
test_info (test_logger.test_logger.TestLogger) ... ok
test_record_metric (test_logger.test_logger.TestLogger) ... ok
test_warn (test_logger.test_logger.TestLogger) ... ok
test_concrete_queue_has_abstract_methods_implemented (test_queue.abstract.test_queue_abstract.TestQueueAbstract) ... ok
test_concrete_queue_inherits_from_queue_abstract (test_queue.abstract.test_queue_abstract.TestQueueAbstract) ... ok
test_azure_provider_invalid_connection_string (test_queue.config.test_queue_config.TestConfig) ... ok
test_azure_provider_missing_queue_name (test_queue.config.test_queue_config.TestConfig) ... ok
test_azure_provider_valid_connection_string (test_queue.config.test_queue_config.TestConfig) ... ok
test_non_azure_provider (test_queue.config.test_queue_config.TestConfig) ... ok
test_add_message_to_queue (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_add_message_to_queue_no_data (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_data_from_invalid_string (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_data_from_valid_string (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_get_items (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_remove_message_from_empty_queue (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_remove_message_from_queue (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_send_queue (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_to_dict (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_validate_data (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_validate_data_invalid_type (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_validate_string (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_validate_string_invalid_type (test_queue.models.test_queue_message.QueueMessageTestCase) ... ok
test_add_message_to_queue (test_queue.test_local_queue.TestLocalQueue) ... ok
test_add_message_to_queue_with_no_data (test_queue.test_local_queue.TestLocalQueue) ... ok
test_empty_queue (test_queue.test_local_queue.TestLocalQueue) ... ok
test_get_items_from_queue (test_queue.test_local_queue.TestLocalQueue) ... ok
test_remove_message_from_queue (test_queue.test_local_queue.TestLocalQueue) ... ok
test_send_with_data (test_queue.test_local_queue.TestLocalQueue) ... 200
ok
test_send_without_data (test_queue.test_local_queue.TestLocalQueue) ... ok
test_add (test_queue.test_queue.TestQueue) ... ok
test_add_no_data (test_queue.test_queue.TestQueue) ... ok
test_empty (test_queue.test_queue.TestQueue) ... ok
test_get_items (test_queue.test_queue.TestQueue) ... ok
test_remove (test_queue.test_queue.TestQueue) ... ok
test_send_no_data (test_queue.test_queue.TestQueue) ... ok
test_send_with_data (test_queue.test_queue.TestQueue) ... ok
test_bad_request_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_conflict_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_forbidden_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_internal_server_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_not_found_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_service_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_timeout_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_too_many_request_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_unauthorized_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_unprocessable_error (test_resource_errors.test_errors.TestServiceErrors) ... ok
test_get_body_text (test_storage.abstract.test_file_entity.TestFileEntity) ... ok
test_get_remote_url (test_storage.abstract.test_file_entity.TestFileEntity) ... ok
test_get_stream (test_storage.abstract.test_file_entity.TestFileEntity) ... ok
test_init (test_storage.abstract.test_file_entity.TestFileEntity) ... ok
test_upload (test_storage.abstract.test_file_entity.TestFileEntity) ... ok
test_get_container (test_storage.abstract.test_storage_client.TestStorageClient) ... ok
test_get_file (test_storage.abstract.test_storage_client.TestStorageClient) ... ok
test_get_file_from_url (test_storage.abstract.test_storage_client.TestStorageClient) ... ok
test_create_file (test_storage.abstract.test_storage_container.TestStorageContainer) ... ok
test_init (test_storage.abstract.test_storage_container.TestStorageContainer) ... ok
test_list_files (test_storage.abstract.test_storage_container.TestStorageContainer) ... ok
test_azure_provider_invalid_connection_string (test_storage.config.test_storage_config.TestConfig) ... ok
test_azure_provider_missing_queue_name (test_storage.config.test_storage_config.TestConfig) ... ok
test_azure_provider_valid_connection_string (test_storage.config.test_storage_config.TestConfig) ... ok
test_non_azure_provider (test_storage.config.test_storage_config.TestConfig) ... ok
test_default_method (test_storage.models.test_config.TestCoreConfig) ... ok
test_init_with_custom_provider (test_storage.models.test_config.TestCoreConfig) ... ok
test_init_with_default_provider (test_storage.models.test_config.TestCoreConfig) ... ok
test_get_body_text (test_storage.test_azure_file_entity.TestAzureFileEntity) ... ok
test_get_remote_url (test_storage.test_azure_file_entity.TestAzureFileEntity) ... ok
test_get_stream (test_storage.test_azure_file_entity.TestAzureFileEntity) ... ok
test_upload (test_storage.test_azure_file_entity.TestAzureFileEntity) ... ok
test_get_container (test_storage.test_azure_storage_client.TestAzureStorageClient) ... ok
test_get_file (test_storage.test_azure_storage_client.TestAzureStorageClient) ... ok
test_get_file_from_url (test_storage.test_azure_storage_client.TestAzureStorageClient) ... ok
test_create_file (test_storage.test_azure_storage_container.TestAzureStorageContainer) ... ok
test_list_files (test_storage.test_azure_storage_container.TestAzureStorageContainer) ... ok
test_list_files_with_name_starts_with (test_storage.test_azure_storage_container.TestAzureStorageContainer) ... ok
test_get_body_text (test_storage.test_local_file_entity.TestLocalFileEntity) ... ok
test_get_remote_url (test_storage.test_local_file_entity.TestLocalFileEntity) ... ok
test_get_stream (test_storage.test_local_file_entity.TestLocalFileEntity) ... ok
test_upload (test_storage.test_local_file_entity.TestLocalFileEntity) ... ok
test_get_container (test_storage.test_local_storage_client.TestLocalStorageClient) ... ok
test_get_container_without_name (test_storage.test_local_storage_client.TestLocalStorageClient) ... ok
test_get_file (test_storage.test_local_storage_client.TestLocalStorageClient) ... ok
test_get_file_from_url (test_storage.test_local_storage_client.TestLocalStorageClient) ... ok
test_create_file (test_storage.test_local_storage_container.LocalStorageContainerTests) ... ok
test_list_files (test_storage.test_local_storage_container.LocalStorageContainerTests) ... ok
test_init (test_topic.abstract.test_topic_abstract.TestDerivedTopic) ... ok
test_publish (test_topic.abstract.test_topic_abstract.TestDerivedTopic) ... ok
test_subscribe (test_topic.abstract.test_topic_abstract.TestDerivedTopic) ... ok
test_azure_provider_invalid_connection_string (test_topic.config.test_topic_config.TestConfig) ... ok
test_azure_provider_logging_levels (test_topic.config.test_topic_config.TestConfig) ... ok
test_azure_provider_valid_connection_string (test_topic.config.test_topic_config.TestConfig) ... ok
test_non_azure_provider (test_topic.config.test_topic_config.TestConfig) ... ok
test_sender_creation (test_topic.config.test_topic_config.TestConfig) ... ok
test_publish (test_topic.test_local_topic.TestLocalTopic) ... ok
test_subscribe_with_subscription (test_topic.test_local_topic.TestLocalTopic) ... ok
test_publish (test_topic.test_topic.TestTopic) ... ok
test_subscribe_with_subscription (test_topic.test_topic.TestTopic) ... ok

----------------------------------------------------------------------
Ran 174 tests in 8.175s

OK
```