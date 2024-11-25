import unittest
from unittest.mock import MagicMock
from src.python_ms_core.core.resource_errors.errors import (
    ServiceError, BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError,
    TimeOutError, ConflictError, UnProcessableError, TooManyRequestError, InternalServerError
)

from src.python_ms_core.core.resource_errors import ExceptionHandler, parse_error

from azure.servicebus.exceptions import AutoLockRenewFailed, AutoLockRenewTimeout, MessageAlreadySettled, \
    MessageLockLostError, MessageNotFoundError, MessageSizeExceededError, MessagingEntityAlreadyExistsError, \
    MessagingEntityDisabledError, MessagingEntityNotFoundError, OperationTimeoutError, ServiceBusAuthenticationError, \
    ServiceBusAuthorizationError, ServiceBusCommunicationError, ServiceBusConnectionError, ServiceBusError, \
    ServiceBusQuotaExceededError, ServiceBusServerBusyError, SessionCannotBeLockedError, SessionLockLostError

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ServiceRequestError, \
    ResourceNotFoundError, AzureError


class TestExceptionHandler(unittest.TestCase):

    def setUp(self):
        self.mock_function = MagicMock()

    def test_service_error(self):
        error_data = {
            'message': 'Error occurred',
            'status_code': 400,
            'description': 'Error description'
        }
        error = ServiceError(error_data)

        self.assertEqual(error.message, 'Error occurred')
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.description, 'Error description')

    def test_bad_request_error(self):
        error_data = {
            'message': 'Bad request',
            'status_code': 400,
            'description': 'Bad request description'
        }
        error = BadRequestError(error_data)

        self.assertEqual(error.message, 'Bad request')
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.description, 'Bad request description')

    def test_unauthorized_error(self):
        error_data = {
            'message': 'Unauthorized',
            'status_code': 401,
            'description': 'Unauthorized description'
        }
        error = UnauthorizedError(error_data)

        self.assertEqual(error.message, 'Unauthorized')
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.description, 'Unauthorized description')

    def test_forbidden_error(self):
        error_data = {
            'message': 'Forbidden',
            'status_code': 403,
            'description': 'Forbidden description'
        }
        error = ForbiddenError(error_data)

        self.assertEqual(error.message, 'Forbidden')
        self.assertEqual(error.status_code, 403)
        self.assertEqual(error.description, 'Forbidden description')

    def test_not_found_error(self):
        error_data = {
            'message': 'Not found',
            'status_code': 404,
            'description': 'Not found description'
        }
        error = NotFoundError(error_data)

        self.assertEqual(error.message, 'Not found')
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.description, 'Not found description')

    def test_timeout_error(self):
        error_data = {
            'message': 'Timeout',
            'status_code': 408,
            'description': 'Timeout description'
        }
        error = TimeOutError(error_data)

        self.assertEqual(error.message, 'Timeout')
        self.assertEqual(error.status_code, 408)
        self.assertEqual(error.description, 'Timeout description')

    def test_conflict_error(self):
        error_data = {
            'message': 'Conflict',
            'status_code': 409,
            'description': 'Conflict description'
        }
        error = ConflictError(error_data)

        self.assertEqual(error.message, 'Conflict')
        self.assertEqual(error.status_code, 409)
        self.assertEqual(error.description, 'Conflict description')

    def test_unprocessable_error(self):
        error_data = {
            'message': 'Unprocessable',
            'status_code': 422,
            'description': 'Unprocessable description'
        }
        error = UnProcessableError(error_data)

        self.assertEqual(error.message, 'Unprocessable')
        self.assertEqual(error.status_code, 422)
        self.assertEqual(error.description, 'Unprocessable description')

    def test_too_many_request_error(self):
        error_data = {
            'message': 'Too many requests',
            'status_code': 429,
            'description': 'Too many requests description'
        }
        error = TooManyRequestError(error_data)

        self.assertEqual(error.message, 'Too many requests')
        self.assertEqual(error.status_code, 429)
        self.assertEqual(error.description, 'Too many requests description')

    def test_internal_server_error(self):
        error_data = {
            'message': 'Internal server error',
            'status_code': 500,
            'description': 'Internal server error description'
        }
        error = InternalServerError(error_data)

        self.assertEqual(error.message, 'Internal server error')
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.description, 'Internal server error description')

    def test_autolock_renew_failed(self):
        # Mock AutoLockRenewFailed exception
        self.mock_function.side_effect = AutoLockRenewFailed('AutoLock Renew Failed')

        # Decorate the mock function with the exception handler
        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(BadRequestError):
            decorated_function()

    def test_client_authentication_error(self):
        # Mock ClientAuthenticationError exception
        self.mock_function.side_effect = ClientAuthenticationError('Authentication failed')

        # Decorate the mock function with the exception handler
        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnauthorizedError):
            decorated_function()

    def test_azure_error(self):
        # Mock AzureError exception
        self.mock_function.side_effect = AzureError('Azure Error occurred')

        # Decorate the mock function with the exception handler
        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(NotFoundError):
            decorated_function()

    def test_value_error(self):
        # Mock ValueError exception
        self.mock_function.side_effect = ValueError('Invalid value')

        # Decorate the mock function with the exception handler
        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnProcessableError):
            decorated_function()

    def test_type_error(self):
        # Mock TypeError exception
        self.mock_function.side_effect = TypeError('Type error occurred')

        # Decorate the mock function with the exception handler
        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(ServiceError):
            decorated_function()

    def test_generic_exception(self):
        # Mock a generic exception
        self.mock_function.side_effect = Exception('Some unexpected error')

        # Decorate the mock function with the exception handler
        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(InternalServerError):
            decorated_function()

    def test_no_exception(self):
        # Mock a function that raises no exceptions
        self.mock_function.side_effect = None

        # Decorate the mock function with the exception handler
        decorated_function = ExceptionHandler.decorated(self.mock_function)

        # Call function and check if no error is raised
        decorated_function()
        self.mock_function.assert_called_once()

    def test_autolock_renew_timeout_error(self):
        self.mock_function.side_effect = AutoLockRenewTimeout('AutoLock Renew Timeout')

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(TimeOutError):
            decorated_function()

    def test_message_lock_lost_error(self):
        self.mock_function.side_effect = MessageLockLostError(message={'message': 'Message Lock Lost'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(BadRequestError):
            decorated_function()

    def test_message_not_found_error(self):
        self.mock_function.side_effect = MessageNotFoundError(message={'message': 'Message Not Found'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(NotFoundError):
            decorated_function()

    def test_message_size_exceeded_error(self):
        self.mock_function.side_effect = MessageSizeExceededError(message={'message': 'Message Size Exceeded'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(BadRequestError):
            decorated_function()

    def test_message_entity_already_exists_error(self):
        self.mock_function.side_effect = MessagingEntityAlreadyExistsError(
            message={'message': 'Message Entity Already Exists'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(ConflictError):
            decorated_function()

    def test_message_entity_disabled_error(self):
        self.mock_function.side_effect = MessagingEntityDisabledError(message={'message': 'Message Entity Disabled'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnProcessableError):
            decorated_function()

    def test_message_entity_not_found_error(self):
        self.mock_function.side_effect = MessagingEntityNotFoundError(message={'message': 'Message Entity Not Found'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(NotFoundError):
            decorated_function()

    def test_operation_timeout_error(self):
        self.mock_function.side_effect = OperationTimeoutError(message={'message': 'Operation Timeout'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(TimeOutError):
            decorated_function()

    def test_service_bus_authentication_error(self):
        self.mock_function.side_effect = ServiceBusAuthenticationError(
            message={'message': 'Service Bus Authentication Failed'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(NotFoundError):
            decorated_function()

    def test_service_bus_authorization_error(self):
        self.mock_function.side_effect = ServiceBusAuthorizationError(
            message={'message': 'Service Bus Authorization Failed'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(ForbiddenError):
            decorated_function()

    def test_service_bus_communication_error(self):
        self.mock_function.side_effect = ServiceBusCommunicationError(
            message={'message': 'Service Bus Communication Failed'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnProcessableError):
            decorated_function()

    def test_service_bus_connection_error(self):
        self.mock_function.side_effect = ServiceBusConnectionError(message={'message': 'Service Bus Connection Failed'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(ForbiddenError):
            decorated_function()

    def test_service_bus_quota_exceeded_error(self):
        self.mock_function.side_effect = ServiceBusQuotaExceededError(
            message={'message': 'Service Bus Quota Exceeded Error'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnProcessableError):
            decorated_function()

    def test_service_bus_busy_error(self):
        self.mock_function.side_effect = ServiceBusServerBusyError(message={'message': 'Service Bus Server Busy Error'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnProcessableError):
            decorated_function()

    def test_session_cannot_be_locked_error(self):
        self.mock_function.side_effect = SessionCannotBeLockedError(
            message={'message': 'Session Cannot Be Locked Error'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnProcessableError):
            decorated_function()

    def test_session_lock_lost_error(self):
        self.mock_function.side_effect = SessionLockLostError(message={'message': 'Session Lock Lost Error'})

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnProcessableError):
            decorated_function()

    def test_service_bus_error(self):
        self.mock_function.side_effect = ServiceBusError('Service Bus Error')

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(ForbiddenError):
            decorated_function()

    def test_resource_not_found_error(self):
        self.mock_function.side_effect = ResourceNotFoundError('Service Bus Error')

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(NotFoundError):
            decorated_function()

    def test_http_response_error(self):
        self.mock_function.side_effect = HttpResponseError('Http Response Error')

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnProcessableError):
            decorated_function()

    def test_service_request_error(self):
        self.mock_function.side_effect = ServiceRequestError('Service Request Error')

        decorated_function = ExceptionHandler.decorated(self.mock_function)

        with self.assertRaises(UnProcessableError):
            decorated_function()


class TestParseError(unittest.TestCase):
    def test_simple_error_message(self):
        base_message = "Error"
        error = "Something went wrong"
        result = parse_error(base_message, error)

        self.assertEqual(result['message'], "Error: Something went wrong")
        self.assertEqual(result['status_code'], 0)
        self.assertEqual(result['description'], '')

    def test_error_with_newlines(self):
        base_message = "Error"
        error = "Something went wrong\nStatus code: 500\nDescription: Internal error"
        result = parse_error(base_message, error)

        self.assertEqual(result['message'], "Error: Something went wrong")
        self.assertEqual(result['status_code'], 500)
        self.assertEqual(result['description'], "Internal error")

    def test_error_with_missing_description(self):
        base_message = "Error"
        error = "Something went wrong\nStatus code: 400"
        result = parse_error(base_message, error)

        self.assertEqual(result['message'], "Error: Something went wrong")
        self.assertEqual(result['status_code'], 400)
        self.assertEqual(result['description'], '')

    def test_error_with_no_status_code(self):
        base_message = "Error"
        error = "Something went wrong\nStatus code: \nDescription: Not Found"
        result = parse_error(base_message, error)

        self.assertEqual(result['message'], "Error: Something went wrong")
        self.assertEqual(result['status_code'], 0)
        self.assertEqual(result['description'], "")

    def test_type_error(self):
        base_message = "TypeError"
        error = TypeError("Invalid Type")
        result = parse_error(base_message, error)

        self.assertEqual(result['message'], "TypeError: Invalid Type")
        self.assertEqual(result['status_code'], 0)
        self.assertEqual(result['description'], '')

    def test_malformed_error(self):
        base_message = "Malformed Error"
        error = "Something went wrong\nStatus code: 400\nDescription: Something unexpected"

        # Call parse_error
        result = parse_error(base_message, error)

        # Assertions
        self.assertEqual(result['message'], "Malformed Error: Something went wrong")
        self.assertEqual(result['status_code'], 400)
        self.assertEqual(result['description'], "Something unexpected")

    def test_error_with_extra_newlines(self):
        base_message = "Error"
        error = "Something went wrong\nStatus code: 400\nDescription: Bad Request\nExtra info"
        result = parse_error(base_message, error)

        self.assertEqual(result['message'], "Error: Something went wrong")
        self.assertEqual(result['status_code'], 400)
        self.assertEqual(result['description'], "Bad Request")

    def test_empty_error(self):
        base_message = "Error"
        error = ""
        result = parse_error(base_message, error)

        self.assertEqual(result['message'], "Error: ")
        self.assertEqual(result['status_code'], 0)
        self.assertEqual(result['description'], '')

    def test_error_with_only_status_code_and_description(self):
        base_message = "Error"
        error = "\nStatus code: 500\nDescription: Internal Server Error"
        result = parse_error(base_message, error)

        self.assertEqual(result['message'], "Error: ")
        self.assertEqual(result['status_code'], 500)
        self.assertEqual(result['description'], "Internal Server Error")


class TestServiceErrors(unittest.TestCase):

    def test_service_error_with_args(self):
        error_data = {
            'message': 'Error occurred',
            'status_code': 400,
            'description': 'Error description'
        }

        # Initialize ServiceError
        error = ServiceError(error_data)

        self.assertEqual(error.message, 'Error occurred')
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.description, 'Error description')

    def test_service_error_without_args(self):
        # Initialize ServiceError without arguments
        error = ServiceError()

        self.assertIsNone(error.message)
        self.assertEqual(error.status_code, 400)  # Default status code
        self.assertIsNone(error.description)

    def test_bad_request_error(self):
        error_data = {
            'message': 'Bad request',
            'status_code': 400,
            'description': 'Bad request description'
        }

        # Initialize BadRequestError
        error = BadRequestError(error_data)

        self.assertEqual(error.message, 'Bad request')
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.description, 'Bad request description')

    def test_unauthorized_error(self):
        error_data = {
            'message': 'Unauthorized',
            'status_code': 401,
            'description': 'Unauthorized description'
        }

        # Initialize UnauthorizedError
        error = UnauthorizedError(error_data)

        self.assertEqual(error.message, 'Unauthorized')
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.description, 'Unauthorized description')

    def test_forbidden_error(self):
        error_data = {
            'message': 'Forbidden',
            'status_code': 403,
            'description': 'Forbidden description'
        }

        # Initialize ForbiddenError
        error = ForbiddenError(error_data)

        self.assertEqual(error.message, 'Forbidden')
        self.assertEqual(error.status_code, 403)
        self.assertEqual(error.description, 'Forbidden description')

    def test_not_found_error(self):
        error_data = {
            'message': 'Not found',
            'status_code': 404,
            'description': 'Not found description'
        }

        # Initialize NotFoundError
        error = NotFoundError(error_data)

        self.assertEqual(error.message, 'Not found')
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.description, 'Not found description')

    def test_timeout_error(self):
        error_data = {
            'message': 'Timeout',
            'status_code': 408,
            'description': 'Timeout description'
        }

        # Initialize TimeOutError
        error = TimeOutError(error_data)

        self.assertEqual(error.message, 'Timeout')
        self.assertEqual(error.status_code, 408)
        self.assertEqual(error.description, 'Timeout description')

    def test_conflict_error(self):
        error_data = {
            'message': 'Conflict',
            'status_code': 409,
            'description': 'Conflict description'
        }

        # Initialize ConflictError
        error = ConflictError(error_data)

        self.assertEqual(error.message, 'Conflict')
        self.assertEqual(error.status_code, 409)
        self.assertEqual(error.description, 'Conflict description')

    def test_unprocessable_error(self):
        error_data = {
            'message': 'Unprocessable',
            'status_code': 422,
            'description': 'Unprocessable description'
        }

        # Initialize UnProcessableError
        error = UnProcessableError(error_data)

        self.assertEqual(error.message, 'Unprocessable')
        self.assertEqual(error.status_code, 422)
        self.assertEqual(error.description, 'Unprocessable description')

    def test_too_many_request_error(self):
        error_data = {
            'message': 'Too many requests',
            'status_code': 429,
            'description': 'Too many requests description'
        }

        # Initialize TooManyRequestError
        error = TooManyRequestError(error_data)

        self.assertEqual(error.message, 'Too many requests')
        self.assertEqual(error.status_code, 429)
        self.assertEqual(error.description, 'Too many requests description')

    def test_internal_server_error(self):
        error_data = {
            'message': 'Internal server error',
            'status_code': 500,
            'description': 'Internal server error description'
        }

        # Initialize InternalServerError
        error = InternalServerError(error_data)

        self.assertEqual(error.message, 'Internal server error')
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.description, 'Internal server error description')

if __name__ == '__main__':
    unittest.main()
