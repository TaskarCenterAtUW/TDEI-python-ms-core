from ...abstracts.authorizer_abstract import AuthorizerAbstract
from ...models.permission_request import PermissionRequest
from ....resource_errors import ExceptionHandler


class SimulatedAuthorizer(AuthorizerAbstract):
    def __init__(self, config=None):
        self.config = config

    @ExceptionHandler.decorated
    def has_permission(self, request_params: PermissionRequest):
        return request_params.should_satisfy_all
