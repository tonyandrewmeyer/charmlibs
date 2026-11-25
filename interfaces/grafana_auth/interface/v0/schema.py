"""This file defines the schemas for the provider and requirer sides of the grafana_auth interface."""

from pydantic import BaseModel, ConfigDict, Field, Json


class ProxyAuth(BaseModel):
    """Configuration for Grafana's auth proxy mode.

    The fields are Grafana's `[auth.proxy]` settings; see
    https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/auth-proxy/.
    """

    model_config = ConfigDict(extra='allow')

    enabled: bool = Field(
        default=True,
        description='Whether auth proxy mode is enabled.',
        examples=[True],
    )
    header_name: str = Field(
        description='The HTTP header that has the user name or email address.',
        examples=['X-WEBAUTH-USER'],
    )
    header_property: str = Field(
        description='What the header has in it: `username` or `email`.',
        examples=['username', 'email'],
    )
    auto_sign_up: bool = Field(
        default=True,
        description='Whether to create users that are not in the Grafana database yet.',
        examples=[True, False],
    )
    sync_ttl: int = Field(
        default=60,
        description='How long, in minutes, to cache the user.',
        examples=[60],
    )
    whitelist: list[str] | None = Field(
        default=None,
        description='The IP addresses that auth proxy requests may come from.',
        examples=[['10.1.0.0/16']],
    )
    headers: list[str] | None = Field(
        default=None,
        description='Other headers to sync user attributes from, each in the form `Attribute:Header`.',
        examples=[['Email:X-User-Email', 'Name:X-User-Name']],
    )
    headers_encoded: bool = Field(
        default=False,
        description='Whether non-ASCII header values are encoded with quoted-printable encoding.',
        examples=[False],
    )
    enable_login_token: bool = Field(
        default=False,
        description='Whether Grafana issues a login token after the user is authenticated by the proxy.',
        examples=[False],
    )


class Auth(BaseModel):
    """Authentication configuration, keyed by authentication mode."""

    model_config = ConfigDict(extra='allow')

    proxy: ProxyAuth = Field(
        description='The configuration for auth proxy mode, which is the only mode so far.',
        examples=[{'header_name': 'X-WEBAUTH-USER', 'header_property': 'username'}],
    )


class ProviderAppData(BaseModel):
    """Application databag model for the provider side of the grafana_auth interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'auth': '{"proxy": {"enabled": true, "header_name": "X-WEBAUTH-USER", '
                    '"header_property": "username", "auto_sign_up": true}}',
                },
                {
                    'auth': '{"proxy": {"enabled": true, "header_name": "X-WEBAUTH-USER", '
                    '"header_property": "email", "auto_sign_up": false, "sync_ttl": 30, '
                    '"whitelist": ["10.1.0.0/16"], "headers": ["Email:X-User-Email"], '
                    '"headers_encoded": true, "enable_login_token": false}}',
                },
            ]
        }
    )

    auth: Json[Auth] = Field(
        description='The authentication configuration, with the authentication mode as the top-level key.',
        examples=[
            '{"proxy": {"enabled": true, "header_name": "X-WEBAUTH-USER", "header_property": "username", "auto_sign_up": true}}'
        ],
    )


class RequirerAppData(BaseModel):
    """Application databag model for the requirer side of the grafana_auth interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {'urls': '["grafana:3000"]'},
                {'urls': '["https://grafana.example.com/"]'},
            ]
        }
    )

    urls: Json[list[str]] = Field(
        description='The URLs at which Grafana can be reached.',
        examples=['["grafana:3000"]', '["https://grafana.example.com/"]'],
    )


ProviderUnitData = None
RequirerUnitData = None
