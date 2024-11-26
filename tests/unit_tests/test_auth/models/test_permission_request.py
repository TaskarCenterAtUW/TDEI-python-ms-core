import unittest
from src.python_ms_core.core.auth.models.permission_request import PermissionRequest


class TestPermissionRequest(unittest.TestCase):

    def setUp(self):
        # Sample input values for testing
        self.user_id = "user123"
        self.project_group_id = "project_group_1"
        self.permissions = "read,write"
        self.should_satisfy_all = True

        # Create an instance of PermissionRequest
        self.permission_request = PermissionRequest(
            user_id=self.user_id,
            project_group_id=self.project_group_id,
            permissions=self.permissions,
            should_satisfy_all=self.should_satisfy_all
        )

    # Test initialization
    def test_initialization(self):
        self.assertEqual(self.permission_request.user_id, self.user_id)
        self.assertEqual(self.permission_request.project_group_id, self.project_group_id)
        self.assertEqual(self.permission_request.permissions, self.permissions)
        self.assertEqual(self.permission_request.should_satisfy_all, self.should_satisfy_all)

    # Test getter and setter for user_id
    def test_user_id_property(self):
        new_user_id = "user456"
        self.permission_request.user_id = new_user_id
        self.assertEqual(self.permission_request.user_id, new_user_id)

    # Test getter and setter for project_group_id
    def test_project_group_id_property(self):
        new_project_group_id = "project_group_2"
        self.permission_request.project_group_id = new_project_group_id
        self.assertEqual(self.permission_request.project_group_id, new_project_group_id)

    # Test getter and setter for permissions
    def test_permissions_property(self):
        new_permissions = "read"
        self.permission_request.permissions = new_permissions
        self.assertEqual(self.permission_request.permissions, new_permissions)

    # Test getter and setter for should_satisfy_all
    def test_should_satisfy_all_property(self):
        self.permission_request.should_satisfy_all = False
        self.assertFalse(self.permission_request.should_satisfy_all)

    # Test get_search_params with default values and permissions
    def test_get_search_params_with_permissions(self):
        expected_params = {
            'userId': self.user_id,
            'projectGroupId': self.project_group_id,
            'affirmative': 'true',
            'roles': self.permissions
        }
        self.assertEqual(self.permission_request.get_search_params(), expected_params)

    # Test get_search_params when permissions are None
    def test_get_search_params_without_permissions(self):
        self.permission_request.permissions = None  # Set permissions to None
        expected_params = {
            'userId': self.user_id,
            'projectGroupId': self.project_group_id,
            'affirmative': 'true'
        }
        self.assertEqual(self.permission_request.get_search_params(), expected_params)

    # Test get_search_params when should_satisfy_all is False
    def test_get_search_params_with_false_should_satisfy_all(self):
        self.permission_request.should_satisfy_all = False  # Set should_satisfy_all to False
        expected_params = {
            'userId': self.user_id,
            'projectGroupId': self.project_group_id,
            'affirmative': 'false',
            'roles': self.permissions
        }
        self.assertEqual(self.permission_request.get_search_params(), expected_params)


if __name__ == '__main__':
    unittest.main()
