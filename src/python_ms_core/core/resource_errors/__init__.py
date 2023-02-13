import operator
from functools import wraps
from .errors import BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError, ConflictError, \
    UnProcessableError, TooManyRequestError, ServiceError, TimeOutError, InternalServerError
from azure.servicebus.exceptions import AutoLockRenewFailed, AutoLockRenewTimeout, MessageAlreadySettled, \
    MessageLockLostError, MessageNotFoundError, MessageSizeExceededError, MessagingEntityAlreadyExistsError, \
    MessagingEntityDisabledError, MessagingEntityNotFoundError, OperationTimeoutError, ServiceBusAuthenticationError, \
    ServiceBusAuthorizationError, ServiceBusCommunicationError, ServiceBusConnectionError, ServiceBusError, \
    ServiceBusQuotaExceededError, ServiceBusServerBusyError, SessionCannotBeLockedError, SessionLockLostError

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ServiceRequestError, \
    ResourceNotFoundError, AzureError


def parse_error(base_message, error):
    message = error
    status_code = 0
    description = ''
    if error.__class__ == TypeError:
        error = str(error)
    try:
        complete_message = error.split('\n') if operator.contains(str(error), '\n') else [error]

        if complete_message and len(complete_message) > 0:
            message = complete_message[0]
        if complete_message and len(complete_message) > 1:
            status_code_string = complete_message[1]
            status_code_string = status_code_string.split('Status code: ')
            if len(status_code_string) == 2:
                status_code = int(status_code_string[1])
        if complete_message and len(complete_message) > 2:
            description_string = complete_message[2]
            description_string = description_string.split('Description: ')
            if len(description_string) == 2:
                description = description_string[1]
    except Exception as e:
        pass

    return {
        'message': f'{base_message}: {message}',
        'status_code': status_code,
        'description': description
    }


class ExceptionHandler:
    @staticmethod
    def decorated(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except AutoLockRenewFailed as ex:
                raise BadRequestError(parse_error('AutoLock Renew Failed Error', ex.message))
            except AutoLockRenewTimeout as ex:
                raise TimeOutError(parse_error('AutoLock Renew Timeout Error', ex.message))
            except MessageAlreadySettled as ex:
                raise BadRequestError(parse_error('Message Already Settled Error', ex.message))
            except MessageLockLostError as ex:
                raise BadRequestError(parse_error('Message Lock Lost Error', ex.message))
            except MessageNotFoundError as ex:
                raise NotFoundError(parse_error('Message Not Found Error', ex.message))
            except MessageSizeExceededError as ex:
                raise BadRequestError(parse_error('Message Size Exceeded Error', ex.message))
            except MessagingEntityAlreadyExistsError as ex:
                raise ConflictError(parse_error('Message Entity Already Exists Error', ex.message))
            except MessagingEntityDisabledError as ex:
                raise UnProcessableError(parse_error('Message Entity Disabled Error', ex.message))
            except MessagingEntityNotFoundError as ex:
                raise NotFoundError(parse_error('Message Entity Not Found Error', ex.message))
            except OperationTimeoutError as ex:
                raise TimeOutError(parse_error('Operation Timeout Error', ex.message))
            except ServiceBusAuthenticationError as ex:
                raise NotFoundError(parse_error('Unable to Authenticate Service Bus Error', ex.message))
            except ServiceBusAuthorizationError as ex:
                raise ForbiddenError(parse_error('Unable to Authorization Service Bus Error', ex.message))
            except ServiceBusCommunicationError as ex:
                raise UnProcessableError(parse_error('Service Bus Communication Error', ex.message))
            except ServiceBusConnectionError as ex:
                raise ForbiddenError(parse_error('Service Bus Connection Error', ex.message))
            except ServiceBusQuotaExceededError as ex:
                raise UnProcessableError(parse_error('Service Bus Quota Exceeded Error', ex.message))
            except ServiceBusServerBusyError as ex:
                raise UnProcessableError(parse_error('Service Bus Server Busy Error', ex.message))
            except SessionCannotBeLockedError as ex:
                raise UnProcessableError(parse_error('Session Cannot Be Locked Error', ex.message))
            except SessionLockLostError as ex:
                raise UnProcessableError(parse_error('Session Lock Lost Error', ex.message))
            except ServiceBusError as ex:
                raise ForbiddenError(parse_error('Service Bus Error', ex.message))
            except ClientAuthenticationError as ex:
                raise UnauthorizedError(parse_error('Client Authentication Error', ex.message))
            except ResourceNotFoundError as ex:
                raise NotFoundError(parse_error('Resource Not Found Error', ex.message))
            except HttpResponseError as ex:
                raise UnProcessableError(parse_error('Http Response Error', ex.message))
            except ServiceRequestError as ex:
                raise UnProcessableError(parse_error('Service Request Error', ex.message))
            except AzureError as ex:
                raise NotFoundError(parse_error('Azure Error', ex.message))
            except ValueError as ex:
                raise UnProcessableError(parse_error('UnProcessable Error', ex))
            except TypeError as ex:
                raise ServiceError(parse_error('Service Error', ex))
            except Exception as ex:
                raise InternalServerError(parse_error('Exception', ex))

        return wrapper
