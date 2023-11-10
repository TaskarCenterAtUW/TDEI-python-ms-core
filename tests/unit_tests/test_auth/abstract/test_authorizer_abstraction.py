import unittest
from unittest.mock import MagicMock
from src.python_ms_core.core.auth.abstracts.authorizer_abstract import AuthorizerAbstract
from src.python_ms_core.core.auth.models.permission_request import PermissionRequest


class TestAuthorizerAbstract(unittest.TestCase):

    def test_has_permission(self):
        # Create a mock PermissionRequest object
        request_params = PermissionRequest(
            user_id='SOME_USER_ID',
            project_group_id='SOME_PROJECT_GROUP_ID',
            should_satisfy_all=False,
            permissions=['poc']
        )

        # Implement a concrete subclass for AuthorizerAbstract
        class AuthorizerImplementation(AuthorizerAbstract):
            def __init__(self, config=None):
                super().__init__(config)

            def has_permission(self, request_params: PermissionRequest):
                # Implement the behavior for the has_permission method
                return True  # Return True for testing purposes

        # Instantiate the AuthorizerImplementation class
        authorizer = AuthorizerImplementation()

        # Call the has_permission method with the mock request_params
        result = authorizer.has_permission(request_params)

        # Assert that the result is True
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
