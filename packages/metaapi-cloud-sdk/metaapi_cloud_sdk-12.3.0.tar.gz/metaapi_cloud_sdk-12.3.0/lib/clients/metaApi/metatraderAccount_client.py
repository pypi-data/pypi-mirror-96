from ..metaApi_client import MetaApiClient
from typing_extensions import TypedDict
from typing import List, Union, Optional, Dict
from httpx import Response
from enum import Enum


class Extension(TypedDict):
    """Extension model."""
    id: str
    """Extension id."""
    configuration: Dict
    """Extension configuration."""


class State(Enum):
    """Account state."""
    CREATED = 'CREATED'
    DEPLOYING = 'DEPLOYING'
    DEPLOYED = 'DEPLOYED'
    DEPLOY_FAILED = 'DEPLOY_FAILED'
    UNDEPLOYING = 'UNDEPLOYING'
    UNDEPLOYED = 'UNDEPLOYED'
    UNDEPLOY_FAILED = 'UNDEPLOY_FAILED'
    DELETING = 'DELETING'
    DELETE_FAILED = 'DELETE_FAILED'
    REDEPLOY_FAILED = 'REDEPLOY_FAILED'


class ConnectionStatus(Enum):
    """Account connection status."""
    CONNECTED = 'CONNECTED'
    DISCONNECTED = 'DISCONNECTED'
    DISCONNECTED_FROM_BROKER = 'DISCONNECTED_FROM_BROKER'


class AccountsFilter(TypedDict):

    offset: Optional[int]
    """Search offset (defaults to 0) (must be greater or equal to 0)."""
    limit: Optional[int]
    """Search limit (defaults to 1000) (must be greater or equal to 1 and less or equal to 1000)."""
    version: Optional[Union[List[int], int]]
    """MT version (allowed values are 4 and 5)"""
    type: Optional[Union[List[str], str]]
    """Account type. Allowed values are 'cloud' and 'self-hosted'"""
    state: Optional[Union[List[State], State]]
    """Account state."""
    connectionStatus: Optional[Union[List[ConnectionStatus], ConnectionStatus]]
    """Connection status."""
    query: Optional[str]
    """Searches over _id, name, server and login to match query."""
    provisioningProfileId: Optional[str]
    """Provisioning profile id."""


class MetatraderAccountIdDto(TypedDict):
    """MetaTrader account id model"""

    id: str
    """MetaTrader account unique identifier"""


class MetatraderAccountDto(TypedDict):
    """MetaTrader account model"""

    _id: str
    """Account unique identifier."""
    name: str
    """MetaTrader account human-readable name in the MetaApi app."""
    type: str
    """Account type, can be cloud, cloud-g1, cloud-g2 or self-hosted. Cloud and cloud-g2 are aliases."""
    login: str
    """MetaTrader account number."""
    server: str
    """MetaTrader server which hosts the account."""
    provisioningProfileId: str
    """Id of the account's provisioning profile."""
    application: str
    """Application name to connect the account to. Currently allowed values are MetaApi and AgiliumTrade"""
    magic: int
    """MetaTrader magic to place trades using."""
    state: str
    """Account deployment state. One of CREATED, DEPLOYING, DEPLOYED, UNDEPLOYING, UNDEPLOYED, DELETING"""
    connectionStatus: str
    """Terminal & broker connection status, one of CONNECTED, DISCONNECTED, DISCONNECTED_FROM_BROKER"""
    accessToken: str
    """Authorization token to be used for accessing single account data. Intended to be used in browser API."""
    manualTrades: bool
    """Flag indicating if trades should be placed as manual trades. Default is false."""
    quoteStreamingIntervalInSeconds: float
    """Quote streaming interval in seconds. Set to 0 in order to receive quotes on each tick. Default value is
    2.5 seconds. Intervals less than 2.5 seconds are supported only for G2."""
    tags: Optional[List[str]]
    """MetaTrader account tags."""
    extensions: List[Extension]
    """API extensions."""
    metadata: Dict
    """Extra information which can be stored together with your account."""
    reliability: str
    """Used to increase the reliability of the account. Allowed values are regular and high. Default is regular."""


class NewMetatraderAccountDto(TypedDict):
    """New MetaTrader account model"""

    name: str
    """MetaTrader account human-readable name in the MetaApi app."""
    type: str
    """Account type, can be cloud, cloud-g1, cloud-g2 or self-hosted. cloud-g2 and cloud are aliases. When you
    create MT5 cloud account the type is automatically converted to cloud-g1 because MT5 G2 support is still
    experimental. You can still create MT5 G2 account by setting type to cloud-g2."""
    login: str
    """MetaTrader account number."""
    password: str
    """MetaTrader account password. The password can be either investor password for read-only access or master
    password to enable trading features. Required for cloud account."""
    server: str
    """MetaTrader server which hosts the account."""
    provisioningProfileId: str
    """Id of the account's provisioning profile."""
    application: str
    """Application name to connect the account to. Currently allowed values are MetaApi and AgiliumTrade."""
    magic: int
    """MetaTrader magic to place trades using."""
    manualTrades: bool
    """Flag indicating if trades should be placed as manual trades. Default is false."""
    quoteStreamingIntervalInSeconds: float
    """Quote streaming interval in seconds. Set to 0 in order to receive quotes on each tick. Default value is
    2.5 seconds. Intervals less than 2.5 seconds are supported only for G2."""
    tags: Optional[List[str]]
    """MetaTrader account tags."""
    extensions: List[Extension]
    """API extensions."""
    metadata: Dict
    """Extra information which can be stored together with your account."""
    reliability: str
    """Used to increase the reliability of the account. Allowed values are regular and high. Default is regular."""


class MetatraderAccountUpdateDto(TypedDict):
    """Updated MetaTrader account data"""

    name: str
    """MetaTrader account human-readable name in the MetaApi app."""
    password: str
    """MetaTrader account password. The password can be either investor password for read-only
    access or master password to enable trading features. Required for cloud account"""
    server: str
    """MetaTrader server which hosts the account"""
    manualTrades: bool
    """Flag indicating if trades should be placed as manual trades. Default is false."""
    quoteStreamingIntervalInSeconds: float
    """Quote streaming interval in seconds. Set to 0 in order to receive quotes on each tick. Default value is
    2.5 seconds. Intervals less than 2.5 seconds are supported only for G2."""
    tags: Optional[List[str]]
    """MetaTrader account tags."""
    extensions: List[Extension]
    """API extensions."""
    metadata: Dict
    """Extra information which can be stored together with your account."""


class MetatraderAccountClient(MetaApiClient):
    """metaapi.cloud MetaTrader account API client (see https://metaapi.cloud/docs/provisioning/)

    Attributes:
        _httpClient: HTTP client
        _host: domain to connect to
        _token: authorization token
    """

    async def get_accounts(self, accounts_filter: AccountsFilter = None) -> Response:
        """Retrieves MetaTrader accounts owned by user
        (see https://metaapi.cloud/docs/provisioning/api/account/readAccounts/)

        Args:
            accounts_filter: Optional filter.

        Returns:
            A coroutine resolving with List[MetatraderAccountDto] - MetaTrader accounts found.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('get_accounts')
        opts = {
            'url': f'{self._host}/users/current/accounts',
            'method': 'GET',
            'params': accounts_filter or {},
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def get_account(self, id: str) -> Response:
        """Retrieves a MetaTrader account by id (see https://metaapi.cloud/docs/provisioning/api/account/readAccount/).
        Throws an error if account is not found.

        Args:
            id: MetaTrader account id.

        Returns:
            A coroutine resolving with MetatraderAccountDto - MetaTrader account found.
        """
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}',
            'method': 'GET',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def get_account_by_token(self) -> 'Response[MetatraderAccountDto]':
        """Retrieves a MetaTrader account by token
        (see https://metaapi.cloud/docs/provisioning/api/account/readAccount/). Throws an error if account is
        not found. Method is accessible only with account access token.

        Returns:
            A coroutine resolving with MetaTrader account found.
        """
        if self._is_not_account_token():
            return self._handle_no_access_exception('get_account_by_token')
        opts = {
            'url': f'{self._host}/users/current/accounts/accessToken/{self._token}',
            'method': 'GET'
        }
        return await self._httpClient.request(opts)

    async def create_account(self, account: NewMetatraderAccountDto) -> Response:
        """Starts cloud API server for a MetaTrader account using specified provisioning profile
        (see https://metaapi.cloud/docs/provisioning/api/account/createAccount/).
        It takes some time to launch the terminal and connect the terminal to the broker, you can use the
        connectionStatus field to monitor the current status of the terminal.

        Args:
            account: MetaTrader account to create.

        Returns:
            A coroutine resolving with MetatraderAccountIdDto - an id of the MetaTrader account created.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('create_account')
        opts = {
            'url': f'{self._host}/users/current/accounts',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            },
            'body': account
        }
        return await self._httpClient.request(opts)

    async def deploy_account(self, id: str) -> Response:
        """Starts API server for MetaTrader account. This request will be ignored if the account has already
        been deployed. (see https://metaapi.cloud/docs/provisioning/api/account/deployAccount/)

        Args:
            id: MetaTrader account id to deploy.

        Returns:
            A coroutine resolving when MetaTrader account is scheduled for deployment
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('deploy_account')
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}/deploy',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def undeploy_account(self, id: str) -> Response:
        """Stops API server for a MetaTrader account. Terminal data such as downloaded market history data will
        be preserved. (see https://metaapi.cloud/docs/provisioning/api/account/undeployAccount/)

        Args:
            id: MetaTrader account id to undeploy.

        Returns:
            A coroutine resolving when MetaTrader account is scheduled for undeployment.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('undeploy_account')
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}/undeploy',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def redeploy_account(self, id: str) -> Response:
        """Redeploys MetaTrader account. This is equivalent to undeploy immediately followed by deploy.
        (see https://metaapi.cloud/docs/provisioning/api/account/redeployAccount/)

        Args:
            id: MetaTrader account id to redeploy.

        Returns:
            A coroutine resolving when MetaTrader account is scheduled for redeployment.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('redeploy_account')
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}/redeploy',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def delete_account(self, id: str) -> Response:
        """Stops and deletes an API server for a specified MetaTrader account. The terminal state such as downloaded
        market data history will be deleted as well when you delete the account.
        (see https://metaapi.cloud/docs/provisioning/api/account/deleteAccount/)

        Args:
            id: MetaTrader account id to delete.

        Returns:
            A coroutine resolving when MetaTrader account is scheduled for deletion.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('delete_account')
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}',
            'method': 'DELETE',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def update_account(self, id: str, account: MetatraderAccountUpdateDto) -> Response:
        """Updates existing metatrader account data (see
        https://metaapi.cloud/docs/provisioning/api/account/updateAccount/)

        Args:
            id: MetaTrader account id.
            account: Updated MetaTrader account.

        Returns:
            A coroutine resolving when MetaTrader account is updated.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('update_account')
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}',
            'method': 'PUT',
            'headers': {
                'auth-token': self._token
            },
            'body': account
        }
        return await self._httpClient.request(opts)
