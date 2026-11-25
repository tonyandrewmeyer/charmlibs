# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""This file defines the schemas for the provider and requirer sides of the `oauth` interface."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, Json


class GrantType(str, Enum):
    """The OAuth 2.0 grant types that a client can use."""

    AUTHORIZATION_CODE = 'authorization_code'
    CLIENT_CREDENTIALS = 'client_credentials'
    REFRESH_TOKEN = 'refresh_token'  # noqa: S105
    DEVICE_CODE = 'urn:ietf:params:oauth:grant-type:device_code'


class TokenEndpointAuthMethod(str, Enum):
    """The ways that a client can authenticate with the token endpoint."""

    CLIENT_SECRET_BASIC = 'client_secret_basic'  # noqa: S105
    CLIENT_SECRET_POST = 'client_secret_post'  # noqa: S105


class ProviderAppData(BaseModel):
    """The provider's application databag."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'issuer_url': 'https://example.com/mymodel-hydra',
                    'authorization_endpoint': 'https://example.com/mymodel-hydra/oauth2/auth',
                    'token_endpoint': 'https://example.com/mymodel-hydra/oauth2/token',
                    'introspection_endpoint': (
                        'http://hydra.mymodel.svc.cluster.local:4445/admin/oauth2/introspect'
                    ),
                    'userinfo_endpoint': 'https://example.com/mymodel-hydra/userinfo',
                    'jwks_endpoint': 'https://example.com/mymodel-hydra/.well-known/jwks.json',
                    'scope': 'openid profile email phone',
                    'jwt_access_token': 'True',
                    'groups': 'groups',
                    'client_id': '07b5e6b2-5c5b-4a3e-9f2e-3c1d2b6a7f10',
                    'client_secret_id': 'secret:1ou9idxgecii2pb9cqez',
                },
                {
                    'issuer_url': 'https://idp.example.com',
                    'authorization_endpoint': 'https://idp.example.com/oauth2/auth',
                    'token_endpoint': 'https://idp.example.com/oauth2/token',
                    'introspection_endpoint': 'https://idp.example.com/admin/oauth2/introspect',
                    'userinfo_endpoint': 'https://idp.example.com/userinfo',
                    'jwks_endpoint': 'https://idp.example.com/.well-known/jwks.json',
                    'scope': 'openid profile email phone',
                    'jwt_access_token': 'False',
                    'ca_chain': (
                        '["-----BEGIN CERTIFICATE-----\\nMIIB...\\n-----END CERTIFICATE-----"]'
                    ),
                },
            ]
        }
    )

    issuer_url: str = Field(
        description="The OpenID Connect identity provider's issuer URL.",
        examples=['https://example.com/mymodel-hydra'],
    )
    authorization_endpoint: str = Field(
        description="The URL of the OpenID Connect identity provider's authorization endpoint.",
        examples=['https://example.com/mymodel-hydra/oauth2/auth'],
    )
    token_endpoint: str = Field(
        description="The URL of the OpenID Connect identity provider's token endpoint.",
        examples=['https://example.com/mymodel-hydra/oauth2/token'],
    )
    introspection_endpoint: str = Field(
        description="The URL of the OpenID Connect identity provider's introspection endpoint.",
        examples=['http://hydra.mymodel.svc.cluster.local:4445/admin/oauth2/introspect'],
    )
    userinfo_endpoint: str = Field(
        description="The URL of the OpenID Connect identity provider's userinfo endpoint.",
        examples=['https://example.com/mymodel-hydra/userinfo'],
    )
    jwks_endpoint: str = Field(
        description="The URL of the OpenID Connect identity provider's JWKS endpoint.",
        examples=['https://example.com/mymodel-hydra/.well-known/jwks.json'],
    )
    scope: str = Field(
        description=(
            'The scopes that the OpenID Connect identity provider supports, separated by spaces.'
        ),
        examples=['openid profile email phone'],
    )
    client_id: str | None = Field(
        default=None,
        description="The ID of the requirer's client.",
        examples=['07b5e6b2-5c5b-4a3e-9f2e-3c1d2b6a7f10'],
    )
    client_secret_id: str | None = Field(
        default=None,
        description=(
            "The ID of the Juju secret that holds the client's secret, under the `secret` key."
        ),
        examples=['secret:1ou9idxgecii2pb9cqez'],
    )
    groups: str | None = Field(
        default=None,
        description="The name of the claim that has the user's groups.",
        examples=['groups'],
    )
    ca_chain: Json[list[str]] | None = Field(
        default=None,
        description=(
            "The CA certificates that the provider's certificates are signed with, "
            'as a JSON list of PEM strings.'
        ),
        examples=['["-----BEGIN CERTIFICATE-----\\nMIIB...\\n-----END CERTIFICATE-----"]'],
    )
    jwt_access_token: bool | None = Field(
        default=None,
        description=(
            'Whether the access tokens that the provider issues are JWTs. Written '
            'as `True` or `False`.'
        ),
        examples=['True', 'False'],
    )


class RequirerAppData(BaseModel):
    """The requirer's application databag."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'redirect_uri': 'https://example.com/mymodel-myapp/callback',
                    'audience': '[]',
                    'scope': 'openid email',
                    'grant_types': '["authorization_code"]',
                    'token_endpoint_auth_method': 'client_secret_basic',
                },
                {
                    'redirect_uri': (
                        '["https://example.com/callback", "https://other.example.com/callback"]'
                    ),
                    'audience': '["myapp"]',
                    'scope': 'openid profile',
                    'grant_types': '["authorization_code", "refresh_token"]',
                    'token_endpoint_auth_method': 'client_secret_post',
                },
                {
                    'audience': '[]',
                    'scope': 'openid',
                    'grant_types': '["client_credentials"]',
                    'token_endpoint_auth_method': 'client_secret_basic',
                },
            ]
        }
    )

    redirect_uri: str | Json[list[str]] | None = Field(
        default=None,
        description=(
            "The client's redirect URI, or a JSON list of them. "
            'Required when the client uses the `authorization_code` grant type.'
        ),
        examples=[
            'https://example.com/mymodel-myapp/callback',
            '["https://example.com/callback", "https://other.example.com/callback"]',
        ],
    )
    audience: Json[list[str]] = Field(
        description='The audiences that the client can request for its tokens, as a JSON list.',
        examples=['[]', '["myapp"]'],
    )
    scope: str = Field(
        description=(
            "The scopes that the client wants to use, from the provider's "
            'supported scopes, separated by spaces.'
        ),
        examples=['openid email', 'openid profile email phone'],
    )
    grant_types: Json[list[GrantType]] = Field(
        description='The grant types that the client wants to use, as a JSON list.',
        examples=[
            '["authorization_code"]',
            '["authorization_code", "refresh_token"]',
            '["client_credentials"]',
        ],
    )
    token_endpoint_auth_method: TokenEndpointAuthMethod = Field(
        description='How the client authenticates with the token endpoint.',
        examples=['client_secret_basic', 'client_secret_post'],
    )
    client_id: str | None = Field(
        default=None,
        description='The ID of the client, if the requirer sets one.',
        examples=['myapp-client'],
    )


ProviderUnitData = None
RequirerUnitData = None
