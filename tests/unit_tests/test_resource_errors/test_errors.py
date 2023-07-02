import unittest
from unittest.mock import MagicMock
from src.python_ms_core.core.resource_errors.errors import (
    ServiceError, BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError,
    TimeOutError, ConflictError, UnProcessableError, TooManyRequestError, InternalServerError
)


class TestServiceErrors(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
