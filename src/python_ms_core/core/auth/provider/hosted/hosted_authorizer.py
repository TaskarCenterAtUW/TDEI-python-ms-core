import requests
from requests.models import PreparedRequest
from ...abstracts.authorizer_abstract import AuthorizerAbstract
from ...models.permission_request import PermissionRequest
from ....resource_errors import ExceptionHandler


class HostedAuthorizer(AuthorizerAbstract):
    def __init__(self, config=None):
        self.config = config

    @ExceptionHandler.decorated
    def has_permission(self, request_params: PermissionRequest):
        if request_params.permissions and len(request_params.permissions) > 0:
            url = self.config.auth_url or None
            if url:
                req = PreparedRequest()
                req.prepare_url(url, request_params.get_search_params())
                response = requests.get(req.url)
                return response.json()
            else:
                raise ValueError('No API url provided')
        else:
            raise ValueError('No roles provided')
