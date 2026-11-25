"""This file defines the schemas for the provider and requirer sides of the `kratos_external_idp` interface."""

import textwrap
from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, Json, model_validator


class Provider(Enum):
    microsoft = "microsoft"
    apple = "apple"
    generic = "generic"
    auth0 = "auth0"
    google = "google"
    facebook = "facebook"
    github = "github"
    gitlab = "gitlab"
    slack = "slack"
    spotify = "spotify"
    discord = "discord"
    twitch = "twitch"
    netid = "netid"
    yandex = "yandex"
    vk = "vk"
    dingtalk = "dingtalk"


class SecretBackend(Enum):
    relation = "relation"
    secret = "secret"
    vault = "vault"


class ExternalIdpProvider(BaseModel):
    client_id: str = Field(
        description="The client ID that the external identity provider issued for Kratos.",
        examples=["client_id"],
    )
    client_secret: str | None = Field(
        default=None,
        description="The client secret that the external identity provider issued for Kratos. Not used with the `apple` provider.",
        examples=["cl1ent-s3cRet"],
    )
    secret_backend: SecretBackend = Field(
        description="Where the client secret and private key are stored. Only `relation`, which puts them in this databag, is implemented.",
        examples=["relation"],
    )
    provider: Provider = Field(
        description="The type of the external identity provider.",
        examples=["microsoft", "generic", "apple"],
    )
    scope: str | None = Field(
        default=None,
        description="The scopes to request from the external identity provider, separated by spaces.",
        examples=["profile email address phone", "user:email"],
    )
    provider_id: str | None = Field(
        default=None,
        description="The ID for Kratos to use for this identity provider.",
        examples=["microsoft", "my-idp"],
    )
    label: str | None = Field(
        default=None,
        description="The name to show users for this identity provider.",
        examples=["Microsoft", "My IdP"],
    )
    jsonnet_mapper: str | None = Field(
        default=None,
        description=(
            "A jsonnet file that will be used to map the external claims to Kratos' claims. "
            "For more info see https://www.ory.sh/docs/kratos/reference/jsonnet."
        ),
        examples=[
            textwrap.dedent(
                """
        local claims = {
            email_verified: false,
        } + std.extVar('claims');

        {
            identity: {
            traits: {
                [if 'email' in claims && claims.email_verified then 'email' else null]: claims.email,
                [if 'name' in claims then 'name' else null]: claims.name,
                [if 'given_name' in claims then 'given_name' else null]: claims.given_name,
                [if 'family_name' in claims then 'family_name' else null]: claims.family_name,
            },
            },
        }
        """
            )
        ],
    )
    tenant_id: str | None = Field(
        default=None,
        description="The Microsoft tenant. Required with, and only allowed with, the `microsoft` provider.",
        examples=["4242424242424242"],
    )
    private_key: str | None = Field(
        default=None,
        description="The private key for Sign in with Apple. Required with, and only allowed with, the `apple` provider.",
        examples=["-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"],
    )
    private_key_id: str | None = Field(
        default=None,
        description="The ID of the private key for Sign in with Apple. Required with, and only allowed with, the `apple` provider.",
        examples=["ABC123DEFG"],
    )
    team_id: str | None = Field(
        default=None,
        description="The Apple Developer team ID. Required with, and only allowed with, the `apple` provider.",
        examples=["TEAM123456"],
    )
    issuer_url: str | None = Field(
        default=None,
        description="The issuer URL of the external identity provider. Required with, and only allowed with, the `generic` and `auth0` providers.",
        examples=["https://idp.example.com", "https://example.auth0.com"],
    )

    @model_validator(mode="after")
    def validate_provider_fields(self) -> "ExternalIdpProvider":
        if self.provider != Provider.apple and not self.client_secret:
            raise ValueError(f"`client_secret` is required with provider {self.provider.value}")

        for fields, providers in (
            (("tenant_id",), (Provider.microsoft,)),
            (("private_key", "private_key_id", "team_id"), (Provider.apple,)),
            (("issuer_url",), (Provider.generic, Provider.auth0)),
        ):
            for field in fields:
                value = getattr(self, field)
                if value and self.provider not in providers:
                    raise ValueError(f"`{field}` not allowed with provider: {self.provider.value}")
                if not value and self.provider in providers:
                    raise ValueError(f"`{field}` is required with provider {self.provider.value}")
        return self


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "providers": '[{"client_id": "client_id", "client_secret": "cl1ent-s3cRet", "secret_backend": "relation", "provider": "microsoft", "scope": "profile email address phone", "tenant_id": "4242424242424242"}]'
                },
                {
                    "providers": '[{"client_id": "client_id", "provider": "apple", "secret_backend": "relation", "scope": "profile email address phone", "team_id": "team_id", "private_key_id": "private_key_id", "private_key": "private_key"}]'
                },
                {
                    "providers": '[{"client_id": "client_id", "provider": "generic", "secret_backend": "relation", "scope": "profile email address phone", "provider_id": "my-idp", "label": "My IdP", "client_secret": "cl1ent-s3cRet", "issuer_url": "https://idp.example.com"}]'
                },
            ]
        }
    )

    providers: Json[list[ExternalIdpProvider]] = Field(
        description="The configuration of the external identity providers, as a JSON list.",
        examples=[
            '[{"client_id": "client_id", "client_secret": "cl1ent-s3cRet", "secret_backend": "relation", "provider": "microsoft", "scope": "profile email address phone", "tenant_id": "4242424242424242"}]',
            '[{"client_id": "client_id", "provider": "github", "secret_backend": "relation", "scope": "user:email", "client_secret": "cl1ent-s3cRet"}]',
        ],
    )


class ExternalIdpRequirer(BaseModel):
    redirect_uri: AnyHttpUrl = Field(
        description="The URL that the external identity provider must redirect users to after they log in.",
        examples=[
            "https://example.com/mymodel-kratos/self-service/methods/oidc/callback/microsoft"
        ],
    )
    provider_id: str = Field(
        description="The ID that Kratos uses for the identity provider.",
        examples=["microsoft", "my-idp"],
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "providers": '[{"redirect_uri": "https://example.com/mymodel-kratos/self-service/methods/oidc/callback/microsoft", "provider_id": "microsoft"}]'
                },
            ]
        }
    )

    providers: Json[list[ExternalIdpRequirer]] = Field(
        description="The redirect URI for each identity provider, as a JSON list.",
        examples=[
            '[{"redirect_uri": "https://example.com/mymodel-kratos/self-service/methods/oidc/callback/microsoft", "provider_id": "microsoft"}]'
        ],
    )


ProviderUnitData = None
RequirerUnitData = None
