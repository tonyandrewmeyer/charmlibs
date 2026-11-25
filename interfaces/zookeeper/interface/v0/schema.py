"""This file defines the schemas for the provider and requirer sides of the zookeeper interface."""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


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
                    "database": "/myappB",
                    "chroot": "/myappB",
                    "endpoints": "10.141.78.133:2181,10.141.78.50:2181,10.141.78.45:2181",
                    "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0",
                    "secret-tls": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog",
                    "data": (
                        '{"database": "/myappB", "requested-secrets":'
                        ' "[\\"username\\", \\"password\\", \\"tls\\", \\"tls-ca\\", \\"uris\\"]"}'
                    ),
                },
                {
                    "database": "/myapp",
                    "chroot": "/myapp",
                    "endpoints": "10.141.78.133:2181,10.141.78.50:2181",
                    "username": "relation-5",
                    "password": "Dy0k2UTfyNt2B13cfe412K7YGs07S4U7",
                    "uris": "10.141.78.133:2181,10.141.78.50:2181/myapp",
                    "tls": "disabled",
                },
            ]
        },
    )

    database: str = Field(
        description=(
            "The zNode that the requirer has been granted access to, which is the parent chroot"
            " for the requirer's data. This might not be the one that it asked for."
        ),
        examples=["/myappB"],
        title="zNode",
    )

    chroot: str | None = Field(
        default=None,
        description="A copy of `database`, for older requirers.",
        examples=["/myappB"],
        title="Chroot",
    )

    endpoints: str = Field(
        description="A comma-separated list of ZooKeeper server addresses, as `host:port`.",
        examples=["10.141.78.133:2181,10.141.78.50:2181,10.141.78.45:2181"],
        title="ZooKeeper endpoints",
    )

    username: str | None = Field(
        default=None,
        description=(
            "The username for connecting to ZooKeeper. Only in the databag when the requirer"
            " doesn't list it in `requested-secrets`; otherwise it's in the `secret-user` secret."
        ),
        examples=["relation-5"],
        title="Username",
    )

    password: str | None = Field(
        default=None,
        description=(
            "The password for connecting to ZooKeeper. Only in the databag when the requirer"
            " doesn't list it in `requested-secrets`; otherwise it's in the `secret-user` secret."
        ),
        examples=["Dy0k2UTfyNt2B13cfe412K7YGs07S4U7"],
        title="Password",
    )

    uris: str | None = Field(
        default=None,
        description=(
            "The ZooKeeper connection string: the server addresses followed by the zNode. Only"
            " in the databag when the requirer doesn't list it in `requested-secrets`;"
            " otherwise it's in the `secret-user` secret."
        ),
        examples=["10.141.78.133:2181,10.141.78.50:2181,10.141.78.45:2181/myappB"],
        title="URIs",
    )

    secret_user: str | None = Field(
        default=None,
        alias="secret-user",
        description=(
            "The ID of a Juju secret with the `username`, `password`, and `uris` keys. Set"
            " instead of those fields when the requirer lists them in `requested-secrets`."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0"],
        title="Credentials secret ID",
    )

    tls: str | None = Field(
        default=None,
        description=(
            "Whether ZooKeeper uses TLS: `enabled` or `disabled`. Only in the databag when the"
            " requirer doesn't list it in `requested-secrets`; otherwise it's in the"
            " `secret-tls` secret."
        ),
        examples=["enabled", "disabled"],
        title="TLS",
    )

    secret_tls: str | None = Field(
        default=None,
        alias="secret-tls",
        description=(
            "The ID of a Juju secret with the `tls` key, and the `tls-ca` key with the CA chain"
            " when the provider shares it."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog"],
        title="TLS secret ID",
    )

    secret_extra: str | None = Field(
        default=None,
        alias="secret-extra",
        description=(
            "The ID of a Juju secret with any other fields that the requirer lists in"
            " `requested-secrets`."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/d1qub7fubg2s77p3nja0"],
        title="Extra secret ID",
    )

    version: str | None = Field(
        default=None,
        description="The ZooKeeper version, if the provider shares it.",
        examples=["3.9.2"],
        title="Version",
    )

    data: dict[str, Any] | None = Field(
        default=None,
        description=(
            "The requirer's application databag as the provider last saw it, used by the"
            " library to work out what changed. A JSON object on the wire."
        ),
        examples=[{"database": "/myappB"}],
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
                    "database": "/myappA",
                    "requested-secrets": '["username", "password", "tls", "tls-ca", "uris"]',
                },
                {
                    "database": "/kafka",
                    "chroot": "/kafka",
                    "requested-secrets": '["username","password","tls","tls-ca","uris"]',
                },
                {
                    "database": "/myapp",
                    "extra-user-roles": "cdrwa",
                    "external-node-connectivity": "true",
                    "requested-secrets": (
                        '["username", "password", "tls", "tls-ca", "uris", "read-only-uris",'
                        ' "entity-name", "entity-password"]'
                    ),
                    "provided-secrets": '["mtls-cert"]',
                },
            ]
        },
    )

    database: str = Field(
        description="The zNode that the requirer wants, which is the parent chroot for its data.",
        examples=["/myappA"],
        title="zNode",
    )

    chroot: str | None = Field(
        default=None,
        description=(
            "An older name for `database`, which the provider reads if `database` isn't set."
        ),
        examples=["/kafka"],
        title="Chroot",
    )

    extra_user_roles: str | None = Field(
        default=None,
        alias="extra-user-roles",
        description=(
            "The ZooKeeper ACL permissions that the requirer wants on its zNode, as a string of"
            " `c` (create), `d` (delete), `r` (read), `w` (write), and `a` (admin). The"
            " provider grants `cdrwa` if this isn't set."
        ),
        examples=["cdrwa"],
        title="User roles",
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

    external_node_connectivity: str | None = Field(
        default=None,
        alias="external-node-connectivity",
        description=(
            "`true` if the requirer will connect from outside the Juju model. Written by"
            " data-integrator; ZooKeeper doesn't use it."
        ),
        examples=["true"],
        title="External node connectivity",
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
                        '{"database": "/myappB", "endpoints": "10.141.78.133:2181",'
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
        examples=[{"database": "/myappB", "endpoints": "10.141.78.133:2181"}],
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
