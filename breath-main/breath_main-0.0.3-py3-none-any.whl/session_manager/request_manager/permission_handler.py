from enum import Enum
import operator

from breath_api_interface.request import Request, Response
from breath_main.session_manager.login_manager import UserLevel
from breath_main.session_manager.request_manager.request_handler import RequestHandler


class PermissionRuleType(Enum):
    '''Type of some rule.
    '''

    EQUAL = 1
    MIN = 2

class PermissionInfo:
    '''Information of some permission requirement.

        :ivar rule_type: Rule type of the requirement.
        :type PermissionRuleType: breath.request_manager.permission_handler.PermissionRuleType
        
        :ivar field: Field of the request been required.
        :type field: str
    
        :ivar value: Required value for the field, according to the rule.
        :type field: object
    '''

    def __init__(self, rule_type:PermissionRuleType, field:str, value:object):
        self.rule_type = rule_type
        self.field = field
        self.value = value 


class PermissionHandler(RequestHandler):
    '''
        Checks the permission requirement of the service being requested.

        :ivar _permission_info: Set of permission info of the registered services.
        :type _permission_info: dict[str, dict[str, PermissionInfo]]

        :ivar user_level: Registered level of the actual user.
        :type user_level: breath.session_manager.login_manager.UserLevel
        :ivar _user_level: Registered level of the actual user.
        :type _user_level: breath.session_manager.login_manager.UserLevel
    '''

    def __init__(self, user_level = UserLevel.NO_LOGIN):
        '''PermissionHandler constructor.

            :param user_level: Actual user level of the user
            :type user_level: breath.session_manager.login_manager.UserLevel
        '''
        super().__init__()

        self._permission_info : dict[str, dict[str, list[PermissionInfo]]] = {} #[sevice_name][operation_name]
        self._user_level :UserLevel = user_level

    @property
    def user_level(self):
        return self._user_level
    
    @user_level.setter
    def user_level(self, value:UserLevel):
        self._user_level = value

    def register_service(self, service_name:str, permission_info:dict):
        '''Register the permission info for a service.

            :param service_name: Name of the service beeing registered.
            :type service_name: str

            :param permission_info: Permission info set of the service. Must be a dictionary with the key being the operation, 
            and the value a list of PermissionInfo.
            :type permission_info: dict[str, dict[str, list[PermissionInfo]]]
        '''
        self._permission_info[service_name] = permission_info

    def handle(self, request:Request) -> None:
        '''Validates the request, looking for permission problems

            :param request: Request to validate and pass foward
            :type request: breath_api_interface.request
        '''

        if self._verify_permission(request):
            self._send_for_next(request)
        else:
            response = Response(False)
            request.send_response(response)

    def _verify_permission(self, request:Request) -> bool:
        '''Checks all permission requirements.

            :param request: Request to validate
            :type request: breath_api_interface.request

            :return: True if pass all the requirements. False if otherwise.
            :rtype: bool
        '''

        service = request.service_name
        operation = request.operation_name
        
        if service not in self._permission_info or operation not in self._permission_info[service]:
            return True

        permission_info : PermissionInfo
        for permission_info in self._permission_info[service][operation]:
            if permission_info.field == "user_level":
                value = self._user_level
            else:
                value = request.request_info[permission_info.field]

            function = None

            if permission_info.rule_type == PermissionRuleType.EQUAL:
                function = operator.eq
            elif permission_info.rule_type == PermissionRuleType.MIN:
                function = operator.ge

            if not function(value, permission_info.value):
                return False

        return True