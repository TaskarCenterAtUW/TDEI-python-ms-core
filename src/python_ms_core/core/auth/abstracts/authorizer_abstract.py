from abc import ABC, abstractmethod
from ..models.permission_request import PermissionRequest


class AuthorizerAbstract(ABC):

    @abstractmethod
    def __init__(self, config=None): pass

    @abstractmethod
    def has_permission(self, request_params: PermissionRequest): pass
