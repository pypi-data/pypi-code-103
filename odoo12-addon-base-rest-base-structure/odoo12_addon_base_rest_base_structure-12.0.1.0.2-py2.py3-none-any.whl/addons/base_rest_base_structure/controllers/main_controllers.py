from odoo.addons.base_rest.controllers import main


class BaseRestPublicApiController(main.RestController):
    _root_path = "/api/public/"
    _collection_name = "base_rest.public_services"
    _default_auth = "api_key"


class BaseRestPrivateApiController(main.RestController):
    _root_path = "/api/private/"
    _collection_name = "base_rest.private_services"
    _default_auth = "api_key"
