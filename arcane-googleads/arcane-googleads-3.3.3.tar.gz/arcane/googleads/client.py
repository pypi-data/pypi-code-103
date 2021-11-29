from typing import Dict, Optional, cast
import backoff

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2.credentials import Credentials
from google.api_core.exceptions import ServiceUnavailable
from google.auth.exceptions import RefreshError

from arcane.core.exceptions import GOOGLE_EXCEPTIONS_TO_RETRY, BadRequestError
from arcane.core.types import BaseAccount
from arcane.datastore import Client as DatastoreClient

from .exceptions import GoogleAdsAccountNoAccessException, GoogleAdsAccountException
from .helpers import (
    get_google_ads_account,
    remove_dash,
    _get_user_initialized_client,
    _init_datastore_client,
    get_login_customer_id_and_developer_token
)


_GOOGLE_ADS_VERSION = "v7"


class Client():
     def __init__(self, google_ads_client: GoogleAdsClient, creator_email: Optional[str] = None):
        self.google_ads_client = google_ads_client
        self.creator_email = creator_email


def get_exception_message(account_id: str, access_token: Optional[str] = None) -> str:
    if access_token:
        return F"We cannot access your account with the id: {account_id}. Are you sure you have access and entered correct ID?"
    else:
        return F"We cannot access your account with the id: {account_id} from the Arcane Manager Account. Are you sure you granted access and gave the correct ID?"

# TODO: Delete access token, developer token and login_customer_id logic when AMCC is finished
def get_google_ads_client(
    mcc_credentials_path: Optional[str] = None,
    access_token: Optional[str] = None,
    login_customer_id: Optional[str] = None,
    developer_token: Optional[str] = None,
    google_ads_account: Optional[Dict] = None,
    base_account: Optional[BaseAccount] = None,
    clients_service_url: Optional[str] = None,
    firebase_api_key: Optional[str] = None,
    gcp_credentials_path: Optional[str] = None,
    auth_enabled: bool = True,
    datastore_client: Optional[DatastoreClient] = None,
    gcp_project: Optional[str] = None,
    secret_key_file: Optional[str] = None,
    user_email: Optional[str] = None
) -> Client:
    """Initialize google ads client depending on arguments furnished
    Priority order is: access_token > creator_email (obtained with google_ads_account/google_ads_account_id) > credentials_path
    Args:
        mcc_credentials_path (Optional[str], optional): mcc credentials. Defaults to None.
        access_token (Optional[str], optional): token obtained with client side oauth pattern. Defaults to None.
        login_customer_id (Optional[str], optional): additionnal info needed in client side oauth pattern. Defaults to None.
        developer_token (Optional[str], optional): developer token for accessing the API. Defaults to None.
        google_ads_account (Optional[Dict], optional): Account for which we want to init google ads client. Defaults to None.
        base_account (Optional[BaseAccount], optional): Account information needed to get the account for which we want to init google ads client. Defaults to None.
        clients_service_url: (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        firebase_api_key: (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        gcp_credentials_path: (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        auth_enabled: (bool, optional): Needed for getting goolge ads account if not provided. Defaults to True.
        datastore_client: (Optional[str], optional): Needed for getting google_ads_user_credential. Defaults to None.
        gcp_project: (Optional[str], optional): Needed for getting google_ads_user_credential. Defaults to None.
        secret_key_file: (Optional[str], optional): Needed for decrypting google_ads_user_credential. Defaults to None.
        user_email: (Optional[str], optional): Needed when the account related is not yet created in db. Defaults to None.
    Raises:
        arcane.core.BadRequestError

    Returns:
        Client: Client
    """

    if access_token:
        credentials = Credentials(token=access_token, scopes='https://www.googleapis.com/auth/adwords')
        return Client(GoogleAdsClient(
            credentials,
            developer_token,
            login_customer_id=login_customer_id
        ))
    elif mcc_credentials_path and (google_ads_account or base_account or user_email):
        if user_email:
            creator_email = user_email
        else:
            if google_ads_account is None and base_account is None:
                raise BadRequestError('google_ads_account and base_account should not be None simultaneously')
            if google_ads_account is None:
                base_account = cast(BaseAccount, base_account)
                google_ads_account = get_google_ads_account(
                    base_account=base_account,
                    clients_service_url=clients_service_url,
                    firebase_api_key=firebase_api_key,
                    gcp_credentials_path=gcp_credentials_path,
                    auth_enabled=auth_enabled
                )
            creator_email = google_ads_account.get('creator_email')
        if creator_email:
            _, developer_token = get_login_customer_id_and_developer_token(mcc_credentials_path)
            if not secret_key_file:
                raise BadRequestError('secret_key_file should not be None while using user access protocol')
            elif not developer_token:
                raise BadRequestError('developer_token should not be None while using user access protocol')
            return Client(
                _get_user_initialized_client(
                    user_email=creator_email,
                    secret_key_file=secret_key_file,
                    developer_token=developer_token,
                    gcp_credentials_path=gcp_credentials_path,
                    gcp_project=gcp_project,
                    datastore_client=datastore_client
                ),
                creator_email=creator_email
            )
        return Client(GoogleAdsClient.load_from_storage(mcc_credentials_path))
    # TODO: Clean this elif when updating check access acount in AMCC track
    elif mcc_credentials_path:
        return Client(GoogleAdsClient.load_from_storage(mcc_credentials_path))
    else:
        raise BadRequestError('one of the following arguments must be specified: access_token or (mcc_credentials_path and (google_ads_account or base_account))')


def get_google_ads_service(service_name: str, google_ads_client: GoogleAdsClient, version: str = _GOOGLE_ADS_VERSION):
    return google_ads_client.get_service(service_name, version=version)

@backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
def check_access_account(
    account_id: Optional[str] = None,
    google_ads_account: Optional[Dict] = None,
    base_account: Optional[BaseAccount] = None,
    clients_service_url: Optional[str] = None,
    firebase_api_key: Optional[str] = None,
    gcp_credentials_path: Optional[str] = None,
    mcc_credentials_path: Optional[str] = None,
    access_token: Optional[str] = None,
    login_customer_id: Optional[str] = None,
    developer_token: Optional[str] = None,
    datastore_client: Optional[DatastoreClient] = None,
    gcp_project: Optional[str] = None,
    secret_key_file: Optional[str] = None,
    client: Optional[Client] = None
):
    """Check if we can access to an GAdsAccount stored in database

    Args:
        account_id (Optional[str], optional): Will be removed. Should be only use in pre creation check
        google_ads_account (Optional[Dict], optional): Account for which we want to init google ads client. Defaults to None.
        base_account (Optional[BaseAccount], optional): Account information needed to get the account for which we want to init google ads client. Defaults to None.
        clients_service_url (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        firebase_api_key (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        gcp_credentials_path (Optional[str], optional): Needed for getting goolge ads account if not provided. Defaults to None.
        mcc_credentials_path (Optional[str], optional): mcc credentials. Defaults to None.
        access_token (Optional[str], optional): token obtained with client side oauth pattern. Defaults to None.
        login_customer_id (Optional[str], optional): additionnal info needed in client side oauth pattern. Defaults to None.
        developer_token (Optional[str], optional): developer token for accessing the API. Defaults to None.
        datastore_client: (Optional[str], optional): Needed for get_google_ads_client. Defaults to None.
        gcp_project: (Optional[str], optional): Needed for get_google_ads_client. Defaults to None.
        secret_key_file: (Optional[str], optional): Needed for get_google_ads_client. Defaults to None.
        client: (Optional[Client], optional): google ads client if already initialized
    Raises:
        BadRequestError: Raised when arguments are not good
        GoogleAdsAccountNoAccessException: Raised when we have no access
    """

    # TODO: delete access token, login customer id, and developper token when AMCC is finished
    if access_token:
        google_ads_client = get_google_ads_client(
            access_token=access_token,
            login_customer_id=login_customer_id,
            developer_token=developer_token,
        ).google_ads_client
        if account_id is None:
                raise BadRequestError('account_id should not be None if access token is given')
        _check_access_account_lgq(account_id, google_ads_client)
    else:
        if not client:
            if google_ads_account is None:
                # TODO: Remove this condition when check_access_before_creation will replace check_access_account use in front
                if not account_id:
                    if base_account is None:
                        raise BadRequestError('google_ads_account and base_account should not be None simultanelously')
                    google_ads_account = get_google_ads_account(
                        base_account=base_account,
                        clients_service_url=clients_service_url,
                        firebase_api_key=firebase_api_key,
                        gcp_credentials_path=gcp_credentials_path
                    )
                    creator_email = google_ads_account.get('creator_email')
                else:
                    creator_email = None
            else:
                creator_email = google_ads_account.get('creator_email')
            google_ads_client = get_google_ads_client(
                mcc_credentials_path=mcc_credentials_path,
                google_ads_account=google_ads_account,
                clients_service_url=clients_service_url,
                firebase_api_key=firebase_api_key,
                gcp_credentials_path=gcp_credentials_path,
                datastore_client=datastore_client,
                gcp_project=gcp_project,
                secret_key_file=secret_key_file
            ).google_ads_client
        else:
            google_ads_client = client.google_ads_client
            creator_email = client.creator_email
            if base_account is None:
                        raise BadRequestError('base_account should not be None when google ads client is given')
            account_id = base_account['id']
        try:
            # TODO: Remove the next four lines. Should always uses google_ads_account['id'] when check_access_before_creation will replace check_access_account use in front
            if google_ads_account is not None:
                account_id = google_ads_account['id']
            if account_id is None:
                raise BadRequestError('account_id and google_ads_account should not be None simultanelously ')
            account_id = account_id
            _check_access_account_lgq(account_id, google_ads_client)
        except GoogleAdsAccountNoAccessException:
            if creator_email:
                message = f"{creator_email} has no longer access to this account."
            else:
                message = "Arcane's Google Ads Manager Account no longer has access to this account."
            raise GoogleAdsAccountNoAccessException(message)
        except (ServiceUnavailable, RefreshError) as err:
            if 'Token has been expired' in str(err) and creator_email:
                raise GoogleAdsAccountNoAccessException(f"{creator_email} authorization has expired.")
            raise



def check_access_before_creation(
    account_id: str,
    user_email: str,
    secret_key_file: str,
    gcp_credentials_path: str,
    gcp_project: str,
    login_customer_id: str,
    developer_token: str,
) -> bool:
    """Check if user identified by its email and our mcc have access or not to an account

    Args:
        account_id (str): Account to check if user has access
        user_email (str): user email
        secret_key_file (str): Path to rsa key to decrypt user credentials stored in datastore
        gcp_credentials_path (str): Needed for getting credentials stored in datastore
        gcp_project (str): Needed for getting credentials stored in datastore
        login_customer_id (str): additionnal info needed in client side oauth pattern
        developer_token (str): developer token for accessing the API.

    Raises:
        GoogleAdsAccountNoAccessException
        GoogleAdsException

    Returns:
        bool: our mcc does it have access
    """
    mcc_access = False
    user_access = False

    datastore_client = _init_datastore_client(gcp_credentials_path, gcp_project)

    ## First step: Check if user have direct access
    try:
        client_initialized_with_user_direct_access = _get_user_initialized_client(
            user_email=user_email,
            secret_key_file=secret_key_file,
            developer_token=developer_token,
            gcp_credentials_path=gcp_credentials_path,
            gcp_project=gcp_project,
            datastore_client=datastore_client
        )
        _check_access_account_lgq(account_id, client_initialized_with_user_direct_access)
        user_access = True
    except GoogleAdsAccountNoAccessException:
        pass

    ## Second step: Check if user have access via our mcc (meaning that our mcc have access)
    try:
        client_initialized_with_user_access_via_mcc = _get_user_initialized_client(
            user_email=user_email,
            secret_key_file=secret_key_file,
            developer_token=developer_token,
            gcp_credentials_path=gcp_credentials_path,
            gcp_project=gcp_project,
            datastore_client=datastore_client,
            login_customer_id=login_customer_id
        )
        _check_access_account_lgq(account_id, client_initialized_with_user_access_via_mcc)
        mcc_access = True
    except GoogleAdsAccountNoAccessException:
        if not user_access:
            raise GoogleAdsAccountNoAccessException("You don't have access to this Google Ads account, you cannot link it to SmartFeeds. Please ask someone else who have access to do the linking")
    return mcc_access


def _check_access_account_lgq(google_ads_account_id: str, google_ads_client: GoogleAdsClient):

    account_id = remove_dash(google_ads_account_id)
    google_ads_service = get_google_ads_service('GoogleAdsService', google_ads_client)

    query = f"""
        SELECT
          customer.manager
        FROM customer
        WHERE customer.id = '{account_id}'"""
    search_query = google_ads_client.get_type(
        "SearchGoogleAdsRequest"
    )
    search_query.customer_id = account_id
    search_query.query = query
    try:
        response = list(google_ads_service.search(search_query))
        if len(response) == 0:
            raise GoogleAdsAccountException(f"We cannot find this account ({google_ads_account_id}). Are you sure you entered the correct id?")
        response = response[0]
    except (GoogleAdsException, GoogleAdsAccountException) as err:
        if "USER_PERMISSION_DENIED" in str(err):
            raise GoogleAdsAccountNoAccessException
        else:
            raise GoogleAdsAccountException(f"We cannot find this account ({google_ads_account_id}). Are you sure you entered the correct id?")
    if response.customer.manager:
        raise GoogleAdsAccountException('This account ID is a MCC. Please enter a Google Ads Account.')
