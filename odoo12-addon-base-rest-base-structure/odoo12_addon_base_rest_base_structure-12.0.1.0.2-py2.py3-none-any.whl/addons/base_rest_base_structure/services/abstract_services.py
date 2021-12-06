from odoo.addons.component.core import AbstractComponent

class BaseRestPublicService(AbstractComponent):
    _name = "base.rest.public_abstract_service"
    _inherit = "base.rest.service"
    _collection = "base_rest.public_services"
    _description = """
        Base Rest Public Services
    """

class BaseRestPrivateService(AbstractComponent):
    _name = "base.rest.private_abstract_service"
    _inherit = "base.rest.service"
    _collection = "base_rest.private_services"
    _description = """
        Base Rest Private Services
    """
