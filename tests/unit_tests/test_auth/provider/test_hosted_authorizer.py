import unittest
from unittest.mock import MagicMock, patch
import requests
from src.python_ms_core.core.auth.provider.hosted.hosted_authorizer import HostedAuthorizer
from src.python_ms_core.core.auth.models.permission_request import PermissionRequest
from src.python_ms_core.core.resource_errors import UnProcessableError


class TestHostedAuthorizer(unittest.TestCase):

    def test_has_permission_with_valid_permissions(self):
        config = MagicMock()
        config.auth_url = 'https://example.com/api/auth'

        user_id = '123'
        project_group_id = '456'
        permissions = ['poc']
        should_satisfy_all = True

        request_params = PermissionRequest(user_id, project_group_id, permissions, should_satisfy_all)

        authorizer = HostedAuthorizer(config)
        response_data = {'status': 'success'}
        requests.get = MagicMock(return_value=MagicMock(json=MagicMock(return_value=response_data)))

        result = authorizer.has_permission(request_params)

        self.assertEqual(result, response_data)

    def test_has_permission_with_invalid_permissions(self):
        config = MagicMock()
        config.auth_url = 'https://example.com/api/auth'

        user_id = '123'
        project_group_id = '456'
        permissions = []
        should_satisfy_all = True

        request_params = PermissionRequest(user_id, project_group_id, permissions, should_satisfy_all)

        authorizer = HostedAuthorizer(config)

        with self.assertRaises(UnProcessableError) as context:
            authorizer.has_permission(request_params)

        expected_error_message = 'No roles provided'
        self.assertIn(expected_error_message, str(context.exception))

    def test_has_permission_with_missing_auth_url(self):
        config = MagicMock()
        config.auth_url = ''

        user_id = '123'
        project_group_id = '456'
        permissions = ['poc']
        should_satisfy_all = True

        request_params = PermissionRequest(user_id, project_group_id, permissions, should_satisfy_all)

        authorizer = HostedAuthorizer(config)

        with self.assertRaises(UnProcessableError) as context:
            authorizer.has_permission(request_params)

        expected_error_message = 'No API url provided'
        self.assertIn(expected_error_message, str(context.exception))


if __name__ == '__main__':
    unittest.main()
