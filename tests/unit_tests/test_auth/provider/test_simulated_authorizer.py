import unittest
from unittest.mock import MagicMock
from src.python_ms_core.core.auth.abstracts.authorizer_abstract import AuthorizerAbstract
from src.python_ms_core.core.auth.models.permission_request import PermissionRequest
from src.python_ms_core.core.auth.provider.simulated.simulated_authorizer import SimulatedAuthorizer


class TestSimulatedAuthorizer(unittest.TestCase):

    def test_has_permission_should_return_should_satisfy_all(self):
        config = MagicMock()
        request_params = PermissionRequest('123', '456', permissions=['poc'], should_satisfy_all=True)
        authorizer = SimulatedAuthorizer(config)

        result = authorizer.has_permission(request_params)

        self.assertTrue(result)

    def test_has_permission_should_return_should_satisfy_none(self):
        config = MagicMock()
        request_params = PermissionRequest('123', '456', permissions=['poc'], should_satisfy_all=False)
        authorizer = SimulatedAuthorizer(config)

        result = authorizer.has_permission(request_params)

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
