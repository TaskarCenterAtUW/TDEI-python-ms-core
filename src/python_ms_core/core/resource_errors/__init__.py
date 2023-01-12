import azure
from functools import wraps
from .errors import BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError, ConflictError, \
    UnProcessableError, TooManyRequestError, ServiceError, TimeOutError


class ExceptionHandler:
    @staticmethod
    def decorated(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except azure.servicebus.exceptions.AutoLockRenewFailed as ex:
                raise BadRequestError(f'AutoLock Renew Failed Error: {ex}')
            except azure.servicebus.exceptions.AutoLockRenewTimeout as ex:
                raise TimeOutError(f'AutoLock Renew Timeout Error: {ex}')
            except azure.servicebus.exceptions.MessageAlreadySettled as ex:
                raise BadRequestError(f'Message Already Settled Error: {ex}')
            except azure.servicebus.exceptions.MessageLockLostError as ex:
                raise BadRequestError(f'Message Lock Lost Error: {ex}')
            except azure.servicebus.exceptions.MessageNotFoundError as ex:
                raise NotFoundError(f'Message Not Found Error: {ex}')
            except azure.servicebus.exceptions.MessageSizeExceededError as ex:
                raise BadRequestError(f'Message Size Exceeded Error: {ex}')
            except azure.servicebus.exceptions.MessagingEntityAlreadyExistsError as ex:
                raise ConflictError(f'Message Entity Already Exists Error: {ex}')
            except azure.servicebus.exceptions.MessagingEntityDisabledError as ex:
                raise UnProcessableError(f'Message Entity Disabled Error: {ex}')
            except azure.servicebus.exceptions.MessagingEntityNotFoundError as ex:
                raise NotFoundError(f'Message Entity Not Found Error: {ex}')
            except azure.servicebus.exceptions.OperationTimeoutError as ex:
                raise TimeOutError(f'Operation Timeout Error: {ex}')
            except azure.servicebus.exceptions.ServiceBusAuthenticationError as ex:
                raise UnauthorizedError(f'Unable to Authenticate Service Bus Error: {ex}')
            except azure.servicebus.exceptions.ServiceBusAuthorizationError as ex:
                raise ForbiddenError(f'Unable to Authorization Service Bus Error: {ex}')
            except azure.servicebus.exceptions.ServiceBusCommunicationError as ex:
                raise UnProcessableError(f'Service Bus Communication Error: {ex}')
            except azure.servicebus.exceptions.ServiceBusConnectionError as ex:
                raise ForbiddenError(f'Service Bus Connection Error: {ex}')
            except azure.servicebus.exceptions.ServiceBusError as ex:
                raise ForbiddenError(f'Service Bus Error: {ex}')
            except azure.servicebus.exceptions.ServiceBusQuotaExceededError as ex:
                raise UnProcessableError(f'Service Bus Quota Exceeded Error: {ex}')
            except azure.servicebus.exceptions.ServiceBusServerBusyError as ex:
                raise UnProcessableError(f'Service Bus Server Busy Error: {ex}')
            except azure.servicebus.exceptions.SessionCannotBeLockedError as ex:
                raise UnProcessableError(f'Session Cannot Be Locked Error: {ex}')
            except azure.servicebus.exceptions.SessionLockLostError as ex:
                raise UnProcessableError(f'Session Lock Lost Error: {ex}')
            except ValueError as ex:
                raise UnProcessableError(f'UnProcessable Error: {ex}')
            except TypeError as ex:
                raise ServiceError(f'Service Error: {ex}')
            except Exception as ex:
                raise ServiceError(f'Exception: {ex}')

        return wrapper
