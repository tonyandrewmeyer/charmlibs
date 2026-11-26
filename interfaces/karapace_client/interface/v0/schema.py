"""This file defines the schemas for the provider and requirer sides of the karapace_client interface."""

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class ExtraUserRole(str, Enum):
    admin = "admin"
    user = "user"


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
    """The databag for the provider side of this interface."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "subject": "orders-value",
                    "endpoints": "10.141.78.155:8081,10.141.78.62:8081,10.141.78.186:8081",
                    "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0",
                    "secret-tls": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog",
                    "data": (
                        '{"subject": "orders-value", "extra-user-roles": "user",'
                        ' "requested-secrets": "[\\"username\\", \\"password\\", \\"tls\\", \\"tls-ca\\", \\"uris\\"]"}'
                    ),
                },
                {
                    "subject": "test-subject",
                    "endpoints": "10.141.78.155:8081",
                    "username": "relation-6",
                    "password": "Dy0k2UTfyNt2B13cfe412K7YGs07S4U7",
                    "tls": "disabled",
                    "data": '{"subject": "test-subject", "extra-user-roles": "admin"}',
                },
            ]
        },
    )

    subject: str = Field(
        description=(
            "The subject that the user has been granted access to, as given in the requirer's"
            " `subject` field."
        ),
        examples=["orders-value"],
        title="Subject name",
    )

    endpoints: str = Field(
        description="A comma-separated list of Karapace server addresses, as `host:port`.",
        examples=["10.141.78.155:8081,10.141.78.62:8081,10.141.78.186:8081"],
        title="Karapace server endpoints",
    )

    username: str | None = Field(
        default=None,
        description=(
            "The username for connecting to Karapace. Only in the databag when the requirer"
            " doesn't list it in `requested-secrets`; otherwise it's in the `secret-user` secret."
        ),
        examples=["relation-14"],
        title="Karapace username",
    )

    password: str | None = Field(
        default=None,
        description=(
            "The password for connecting to Karapace. Only in the databag when the requirer"
            " doesn't list it in `requested-secrets`; otherwise it's in the `secret-user` secret."
        ),
        examples=["Dy0k2UTfyNt2B13cfe412K7YGs07S4U7"],
        title="Karapace password",
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

    tls: str | None = Field(
        default=None,
        description=(
            "Whether Karapace uses TLS: `enabled` or `disabled`. Only in the databag when the"
            " requirer doesn't list it in `requested-secrets`; otherwise it's in the"
            " `secret-tls` secret."
        ),
        examples=["enabled", "disabled"],
        title="TLS",
    )

    secret_tls: str | None = Field(
        default=None,
        alias="secret-tls",
        description="The ID of a Juju secret with the `tls` key.",
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog"],
        title="TLS secret ID",
    )

    entity_name: str | None = Field(
        default=None,
        alias="entity-name",
        description=(
            "The name of the custom entity that the requirer asked for with `entity-type`. Only"
            " in the databag when the requirer doesn't list it in `requested-secrets`;"
            " otherwise it's in the `secret-entity` secret."
        ),
        examples=["custom-role"],
        title="Entity name",
    )

    entity_password: str | None = Field(
        default=None,
        alias="entity-password",
        description=(
            "The password of the custom entity. Only in the databag when the requirer doesn't"
            " list it in `requested-secrets`; otherwise it's in the `secret-entity` secret."
        ),
        examples=["Dy0k2UTfyNt2B13cfe412K7YGs07S4U7"],
        title="Entity password",
    )

    secret_entity: str | None = Field(
        default=None,
        alias="secret-entity",
        description="The ID of a Juju secret with the `entity-name` and `entity-password` keys.",
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/d1qub7fubg2s77p3nja0"],
        title="Entity secret ID",
    )

    data: dict[str, Any] | None = Field(
        default=None,
        description=(
            "The requirer's application databag as the provider last saw it, used by the"
            " library to work out what changed. A JSON object on the wire."
        ),
        examples=[{"subject": "orders-value", "extra-user-roles": "user"}],
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
    """The databag for the requirer side of this interface."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "subject": "test-subject",
                    "extra-user-roles": "admin",
                    "requested-secrets": (
                        '["username", "password", "tls", "tls-ca", "uris", "read-only-uris",'
                        ' "entity-name", "entity-password"]'
                    ),
                    "provided-secrets": '["mtls-cert"]',
                },
                {
                    "subject": "orders-value",
                    "extra-user-roles": "user",
                    "requested-secrets": '["username", "password", "tls", "tls-ca", "uris"]',
                },
            ]
        },
    )

    subject: str = Field(
        description="The subject that the requirer wants access to.",
        examples=["orders-value"],
        title="Subject name",
    )

    extra_user_roles: str | None = Field(
        default=None,
        alias="extra-user-roles",
        description=(
            "The role that the requirer wants: `admin` or `user`. A requirer that doesn't"
            " write this is given the `user` role."
        ),
        examples=["admin", "user"],
        title="Extra user roles",
    )

    extra_group_roles: str | None = Field(
        default=None,
        alias="extra-group-roles",
        description="A comma-separated list of the roles that the requirer wants for a group entity.",
        examples=["charmed_read"],
        title="Extra group roles",
    )

    entity_type: str | None = Field(
        default=None,
        alias="entity-type",
        description="The type of custom entity that the requirer wants: `USER` or `GROUP`.",
        examples=["USER", "GROUP"],
        title="Entity type",
    )

    entity_permissions: str | None = Field(
        default=None,
        alias="entity-permissions",
        description=(
            "The permissions that the requirer wants for the custom entity, as a JSON list of"
            " objects with `resource_name`, `resource_type`, and `privileges`. The library"
            " writes this string as it's given."
        ),
        examples=[
            '[{"resource_name": "orders-value", "resource_type": "SUBJECT", "privileges": ["READ"]}]'
        ],
        title="Entity permissions",
    )

    requested_secrets: list[str] | None = Field(
        default=None,
        alias="requested-secrets",
        description=(
            "The provider fields that the requirer wants in Juju secrets rather than in the"
            " databag. A JSON array on the wire."
        ),
        examples=[["username", "password", "tls", "tls-ca", "uris"]],
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

    @field_validator("extra_user_roles", mode="before")
    @classmethod
    def _check_role(cls, value: Any) -> Any:
        if isinstance(value, str) and value not in {role.value for role in ExtraUserRole}:
            raise ValueError(f"Role {value} is not valid.")
        return value

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
                        '{"subject": "orders-value", "endpoints": "10.141.78.155:8081",'
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
        examples=[["username", "password", "tls", "tls-ca", "uris"]],
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
        examples=[{"subject": "orders-value", "endpoints": "10.141.78.155:8081"}],
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
