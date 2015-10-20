from heman.api import AuthorizedResource
from heman.auth import check_contract_allowed


class EmpoweringResource(AuthorizedResource):
    method_decorators = (
        AuthorizedResource.method_decorators + [check_contract_allowed]
    )
