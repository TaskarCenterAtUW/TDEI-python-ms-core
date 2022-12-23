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
            except azure.servicebus.exceptions as ex:
                raise BadRequestError('Server could not understand your request. Please try again later.')
            except azure.core.exceptions.ClientAuthenticationError as ex:
                raise UnauthorizedError('Unable to authenticate.')
            except azure.core.exceptions.ResourceExistsError as ex:
                raise NotFoundError('Resource not found')
            except azure.core.exceptions.TooManyRedirectsError as ex:
                raise TooManyRequestError('To many attempts, please try again later')
            except azure.core.exceptions.ServiceRequestError as ex:
                raise UnProcessableError('Request is not processable. Please try again later.')
            except azure.core.exceptions.OperationTimeoutError as ex:
                raise TimeOutError('Request time out. Please try again later.')
            except ValueError as ex:
                raise UnProcessableError(str(ex))
            except Exception as ex:
                print(ex)
                raise ServiceError(str(ex))

        return wrapper
