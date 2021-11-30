from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

from dataclasses_json import DataClassJsonMixin

from common.api.dtos.datetime_field import datetime_field
from common.input_validator import InputValidator


class UserStatusDTO(str, Enum):
    UNCONFIRMED = 'unconfirmed'
    CONFIRMED = 'confirmed'
    ARCHIVED = 'archived'
    COMPROMISED = 'compromised'
    UNKNOWN = 'unknown'
    RESET_REQUIRED = 'reset_required'
    FORCE_CHANGE_PASSWORD = 'force_change_password'


class RoleTypeDTO(str, Enum):
    ADMIN = 'admin'
    READ_ONLY = 'read_only'


@dataclass
class AccessControlGroupDTO(DataClassJsonMixin):
    id: str
    name: str
    created_at: datetime_field()
    updated_at: datetime_field()
    roles: List[RoleTypeDTO] = field(default_factory=list)


@dataclass
class AccessControlUserDTO(DataClassJsonMixin):
    created_at: datetime_field()
    updated_at: datetime_field()
    groups: List[AccessControlGroupDTO] = field(default_factory=list)


@dataclass
class UserDTO(DataClassJsonMixin):
    """
    ---
    properties:
        email:
            type: string
            description:
                The user's email address.
        first_name:
            type: string
            description:
                The user's first name.
        last_name:
            type: string
            description:
                The user's first name.
        created_at:
            type: string
            description:
                The date when the user was first added.
        updated_at:
            type: string
            description:
                The date when the user was last updated.
    """
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    customer_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    status: Optional[UserStatusDTO] = None
    access_control: Optional[AccessControlUserDTO] = None


@dataclass
class UserUpdateDTO(DataClassJsonMixin):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[RoleTypeDTO] = None

    def __post_init__(self):
        InputValidator.validate_user_description(self.first_name, True)
        InputValidator.validate_user_description(self.last_name, True)


@dataclass
class UserRegisterDTO(DataClassJsonMixin):
    email: str
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    utm_campaign_parameters: Optional[str] = None
    captcha_token: Optional[str] = None

    def __post_init__(self):
        InputValidator.validate_email(self.email)
        InputValidator.validate_user_description(self.first_name, allow_none=True)
        InputValidator.validate_user_description(self.last_name, allow_none=True)
        InputValidator.validate_password(self.password)


@dataclass
class UserRegisterWithInvitationDTO(DataClassJsonMixin):
    email: str
    temporary_password: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    captcha_token: Optional[str] = None

    def __post_init__(self):
        InputValidator.validate_email(self.email)
        InputValidator.validate_user_description(self.first_name)
        InputValidator.validate_user_description(self.last_name)
        InputValidator.validate_password(self.password)


@dataclass
class UserInviteDTO(DataClassJsonMixin):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: RoleTypeDTO = RoleTypeDTO.READ_ONLY

    def __post_init__(self):
        InputValidator.validate_email(self.email)
        InputValidator.validate_user_description(self.first_name, True)
        InputValidator.validate_user_description(self.last_name, True)

@dataclass
class UsersInviteDTO(DataClassJsonMixin):
    emails: List[UserInviteDTO]
    captcha_token: Optional[str] = None

@dataclass
class UserUnregisterDTO(DataClassJsonMixin):
    email: str
    password: str

    def __post_init__(self):
        InputValidator.validate_email(self.email)
        InputValidator.validate_password(self.password)


@dataclass
class UserLoginDTO(DataClassJsonMixin):
    email: str
    password: str

    def __post_init__(self):
        InputValidator.validate_email(self.email)
        InputValidator.validate_password(self.password)


@dataclass
class UserResetPasswordDTO(DataClassJsonMixin):
    email: str
    password: str
    confirmation_code: str
    captcha_token: Optional[str] = None

    def __post_init__(self):
        InputValidator.validate_email(self.email)
        self.confirmation_code = self.confirmation_code or ''
        self.confirmation_code = self.confirmation_code.strip()
        InputValidator.validate_confirmation_code(self.confirmation_code)
        InputValidator.validate_password(self.password)


@dataclass
class UserResetPasswordRequestDTO(DataClassJsonMixin):
    email: str
    captcha_token: Optional[str] = None

    def __post_init__(self):
        InputValidator.validate_email(self.email)


@dataclass
class UserChangePasswordDTO(DataClassJsonMixin):
    password: str
    new_password: str

    def __post_init__(self):
        InputValidator.validate_password(self.password)
        InputValidator.validate_password(self.password)


@dataclass
class UserWithTokenDTO(UserDTO):
    id_token: str = None
    access_token: str = None
    expires_in: int = None
    refresh_token: str = None


@dataclass
class ApiKeyDTO(DataClassJsonMixin):
    api_key: str


@dataclass
class UserInvitationSummaryDTO(DataClassJsonMixin):
    email: str
    invitation_sent: bool
    error: Optional[str] = None


@dataclass
class UserResetPasswordRequestSummaryDTO(DataClassJsonMixin):
    email: str
    confirmation_code_sent: bool


@dataclass
class UserConfirmationDTO(DataClassJsonMixin):
    email: str
    confirmation_code: str

    def __post_init__(self):
        InputValidator.validate_email(self.email)
