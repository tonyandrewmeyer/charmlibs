"""This file defines the schemas for the provider and requirer sides of the `connect_client` interface."""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

PLUGIN_URL_NOT_REQUIRED = "NOT-REQUIRED"


class _BareStringDatabag(BaseModel):
    """Base class for databag models that don't strictly JSON encode all entries."""

    @staticmethod
    def __juju_decoder__(value: str) -> str:
        """Pass Juju's string through unmodified to be decoded by individual field validators."""
        return value

    @staticmethod
    def __juju_encoder__(value: str | None) -> str:
        """Convert `None` to "", erasing the value; Ops will error on a non-string."""
        return "" if value is None else value


def _load_json(value: Any) -> Any:
    if not isinstance(value, str):
        return value  # __init__ argument was already deserialized.
    return json.loads(value)


def _dump_json(value: object) -> str | None:
    if value is None:
        return None
    return json.dumps(value)


class ProviderAppData(_BareStringDatabag):
    """The provider's application databag."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "endpoints": "http://10.1.1.100:8083,http://10.1.1.101:8083,http://10.1.1.102:8083",
                    "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0",
                    "secret-tls": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog",
                    "data": (
                        '{"plugin-url": "http://10.1.1.200:8080/route/to/plugin",'
                        ' "requested-secrets": "[\\"username\\", \\"password\\", \\"tls\\", \\"tls-ca\\", \\"uris\\"]"}'
                    ),
                },
                {
                    "endpoints": "http://10.1.1.100:8083",
                    "username": "relation-4",
                    "password": "Dy0k2UTfyNt2B13cfe412K7YGs07S4U7",
                    "data": '{"plugin-url": "NOT-REQUIRED"}',
                },
            ]
        },
    )

    endpoints: str = Field(
        description=(
            "A comma-separated list of Kafka Connect REST endpoints, each including the"
            " protocol (`http` or `https`)."
        ),
        examples=["http://10.1.1.100:8083,http://10.1.1.101:8083,http://10.1.1.102:8083"],
        title="Kafka Connect endpoints",
    )

    username: str | None = Field(
        default=None,
        description=(
            "The username for the Kafka Connect REST interface. Only in the databag when the"
            " requirer doesn't list it in `requested-secrets`; otherwise it's in the"
            " `secret-user` secret."
        ),
        examples=["relation-4"],
        title="Username",
    )

    password: str | None = Field(
        default=None,
        description=(
            "The password for the Kafka Connect REST interface. Only in the databag when the"
            " requirer doesn't list it in `requested-secrets`; otherwise it's in the"
            " `secret-user` secret."
        ),
        examples=["Dy0k2UTfyNt2B13cfe412K7YGs07S4U7"],
        title="Password",
    )

    secret_user: str | None = Field(
        default=None,
        alias="secret-user",
        description=(
            "The ID of a Juju secret with the `username` and `password` keys. Set instead of"
            " `username` and `password` when the requirer lists them in `requested-secrets`."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0"],
        title="Credentials secret ID",
    )

    secret_tls: str | None = Field(
        default=None,
        alias="secret-tls",
        description=(
            "The ID of a Juju secret with the `tls-ca` key, holding the CA chain for the REST"
            " endpoints, when they use HTTPS. Absent when TLS is disabled."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog"],
        title="TLS secret ID",
    )

    data: dict[str, Any] | None = Field(
        default=None,
        description=(
            "The requirer's application databag as the provider last saw it, used by the"
            " library to work out what changed. A JSON object on the wire."
        ),
        examples=[{"plugin-url": "NOT-REQUIRED"}],
        title="Last seen requirer data",
    )

    @field_validator("data", mode="before")
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        return _load_json(value)

    @field_serializer("data")
    def _dump_json(self, value: object) -> str | None:
        return _dump_json(value)


class RequirerAppData(_BareStringDatabag):
    """The requirer's application databag."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "plugin-url": "http://10.1.1.200:8080/route/to/plugin",
                    "requested-secrets": '["username", "password", "tls", "tls-ca", "uris"]',
                },
                {
                    "plugin-url": PLUGIN_URL_NOT_REQUIRED,
                    "requested-secrets": (
                        '["username", "password", "tls", "tls-ca", "uris", "read-only-uris",'
                        ' "entity-name", "entity-password"]'
                    ),
                    "provided-secrets": '["mtls-cert"]',
                },
            ]
        },
    )

    plugin_url: str = Field(
        alias="plugin-url",
        description=(
            "The URL at which the connector plugins that the requirer needs are served, as a"
            f" single tarball, or `{PLUGIN_URL_NOT_REQUIRED}` if it doesn't need any."
        ),
        examples=["http://10.1.1.200:8080/route/to/plugin", PLUGIN_URL_NOT_REQUIRED],
        title="Plugin URL",
    )

    requested_secrets: list[str] | None = Field(
        default=None,
        alias="requested-secrets",
        description=(
            "The provider fields that the requirer wants in Juju secrets rather than in the"
            " databag. A JSON array on the wire."
        ),
        examples=[["username", "password", "tls", "tls-ca"]],
        title="Requested secrets",
    )

    provided_secrets: list[str] | None = Field(
        default=None,
        alias="provided-secrets",
        description=(
            "The requirer fields that the requirer puts in Juju secrets rather than in the"
            " databag. A JSON array on the wire."
        ),
        examples=[["mtls-cert"]],
        title="Provided secrets",
    )

    @field_validator("requested_secrets", "provided_secrets", mode="before")
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        return _load_json(value)

    @field_serializer("requested_secrets", "provided_secrets")
    def _dump_json(self, value: object) -> str | None:
        return _dump_json(value)


class RequirerUnitData(_BareStringDatabag):
    """The requirer's unit databag, written by the library for its own bookkeeping."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "requested-secrets": (
                        '["username", "password", "tls", "tls-ca", "uris", "read-only-uris",'
                        ' "entity-name", "entity-password"]'
                    ),
                    "provided-secrets": '["mtls-cert"]',
                    "data": (
                        '{"endpoints": "http://10.1.1.100:8083",'
                        ' "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0"}'
                    ),
                },
            ]
        },
    )

    requested_secrets: list[str] | None = Field(
        default=None,
        alias="requested-secrets",
        description="A copy of `requested-secrets` from the application databag. A JSON array on the wire.",
        examples=[["username", "password", "tls", "tls-ca"]],
        title="Requested secrets",
    )

    provided_secrets: list[str] | None = Field(
        default=None,
        alias="provided-secrets",
        description="A copy of `provided-secrets` from the application databag. A JSON array on the wire.",
        examples=[["mtls-cert"]],
        title="Provided secrets",
    )

    data: dict[str, Any] | None = Field(
        default=None,
        description=(
            "The provider's application databag as the requirer last saw it, used by the"
            " library to work out what changed. A JSON object on the wire."
        ),
        examples=[{"endpoints": "http://10.1.1.100:8083"}],
        title="Last seen provider data",
    )

    @field_validator("requested_secrets", "provided_secrets", "data", mode="before")
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        return _load_json(value)

    @field_serializer("requested_secrets", "provided_secrets", "data")
    def _dump_json(self, value: object) -> str | None:
        return _dump_json(value)


ProviderUnitData = None
