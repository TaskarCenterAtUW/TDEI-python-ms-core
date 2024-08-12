# Change log

# Version 0.0.21
### New Features and Enhancements
- **Message Lock Renewal:** Implemented a mechanism to automatically renew message locks during processing. This ensures that messages remain active and are not returned to the queue for reprocessing while they are being handled.  
- **Concurrent Message Processing:** Enhanced the system to process messages concurrently using a number of worker threads equal to the number of available CPU cores by default. Users can override this default by specifying the `max_concurrent_messages` parameter, for example, `core.get_topic(topic_name=topic_name, max_concurrent_messages=10)`. This optimization leverages system resources for improved performance and throughput. 
- **Completion Acknowledgement:** Updated the processing flow to wait until message processing is fully completed before sending the acknowledgement of message completion. This change ensures reliable processing and accurate message handling. 
- **Version Tracking:** Introduced a `version.py` file to maintain and track the package version. This addition facilitates version control and package management.
- **Unit Test Updates:** Updated unit test cases to cover the new features and enhancements, ensuring robust testing and quality assurance.
- **Documentation Update:** Updated the README file to reflect the new features and enhancements, providing clearer guidance and information for users.



# 0.0.18
- Adds extra checks in service bus for retries
- Additional logging done if there is no network and  service bus crashes
- Service bus subscription picks up messages even if there is network outtage

### 0.0.17
- Added Unit Test Cases
- Updated Readme file 

### 0.0.16
- Removed extra logs

### 0.0.15
This fixes the inconsistent listening behavior for the subscription of a topic from core.
- Due to the usage of `for message in receiver` logic in the topic, it is unknown when the loop will end and the core will stop listening to the topic.
- This is tried with various combinations and figured out that at probably 4 hours from launch, this happens. The root cause for this is the socket / connection timeout of the underlying amqp client which throws an exception when trying to iterate next message

Fix made:
- The above for loop is kept in an infinite while loop which triggers the creation of the receiver and subsequent listening to the messages. 
- This was tested overnight with messages varying in the time differences (1h to 3h)
- Specific method to look for the fix `start_listening`

Reference task:
[302](https://dev.azure.com/TDEI-UW/TDEI/_workitems/edit/302)


### 0.0.14
- Fixed https://dev.azure.com/TDEI-UW/TDEI/_workitems/edit/302

### 0.0.13
- Removed validation from QueueMassage Class


### 0.0.12
- Added name_starts_with parameter in Storage


### 0.0.11
- Added Local Storage


### 0.0.10
- Added TopicAbstract and TopicConfig to package


### 0.0.9
- Adding files to python package
 

### 0.0.8
- Authorization methods included
- Simulated and Hosted Authorizers implemented
- Examples written for both
- Readme updated appropriately.


### 0.0.7
- Fixed configuration issues
- Fixed all the review comments
- Refactor code
- Removed unused code
- Added local dev env using TDEI-local-server Package
- Added local env support to -
  - Logger
  - Queue
  - Topic
  - Storage

### 0.0.6
- Added get_remote_url function in FileEntity class which will return the uploaded file url

### 0.0.5
- Fixed Storage Blob stream

### 0.0.4
- Fixed threading

### 0.0.3
- Removed blocking call from topic subscription
- Added TODOs and FIXMEs

### 0.0.2
- Added filtered exception handling
- Removed unused packages
- Fixed Topic subscription

### 0.0.1
- Introduces Topic and subscription methods in Core.
- Added methods
    - Core.ge_topic()
- Added classes and methods
    - Topic
        - publish
        - subscribe