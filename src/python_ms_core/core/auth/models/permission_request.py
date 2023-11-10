from typing import Optional
from dataclasses import dataclass


@dataclass
class PermissionRequest:
    user_id: str
    project_group_id: str
    permissions: Optional[str] = None
    should_satisfy_all: bool = False

    def __init__(self, user_id: str, project_group_id: str, permissions: Optional[str] = None, should_satisfy_all: bool = False):
        self._user_id = user_id
        self._project_group_id = project_group_id
        self._permissions = permissions
        self._should_satisfy_all = should_satisfy_all

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def project_group_id(self):
        return self._project_group_id

    @project_group_id.setter
    def project_group_id(self, value):
        self.project_group_id = value

    @property
    def permissions(self):
        return self._permissions

    @permissions.setter
    def permissions(self, value):
        self._permissions = value

    @property
    def should_satisfy_all(self):
        return self._should_satisfy_all

    @should_satisfy_all.setter
    def should_satisfy_all(self, value):
        self._should_satisfy_all = value

    def get_search_params(self):
        affirmative = 'true' if self._should_satisfy_all else 'false'
        params = {
            'userId': self._user_id,
            'projectGroupId': self.project_group_id,
            'affirmative': affirmative
        }
        if self._permissions and len(self._permissions) > 0:
            params['roles'] = self._permissions
        return params

