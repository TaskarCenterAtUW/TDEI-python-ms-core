import unittest
from src.python_ms_core.core.auth.models.permission_request import PermissionRequest


class TestPermissionRequest(unittest.TestCase):

    def test_get_search_params(self):
        user_id = '123'
        org_id = '456'
        permissions = 'read,write'
        should_satisfy_all = True

        request = PermissionRequest(user_id, org_id, permissions, should_satisfy_all)
        search_params = request.get_search_params()

        expected_params = {
            'userId': user_id,
            'agencyId': org_id,
            'affirmative': 'true',
            'roles': permissions
        }

        self.assertEqual(search_params, expected_params)


if __name__ == '__main__':
    unittest.main()
