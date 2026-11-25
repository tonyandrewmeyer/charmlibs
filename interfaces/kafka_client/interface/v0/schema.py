"""This file defines the schemas for the provider and requirer sides of the kafka_client interface."""

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class ExtraUserRole(str, Enum):
    admin = "admin"
    consumer = "consumer"
    producer = "producer"
    manager = "manager"


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
                    "topic": "orders",
                    "endpoints": "10.141.78.155:9092,10.141.78.62:9092,10.141.78.186:9092",
                    "consumer-group-prefix": "relation-14-",
                    "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0",
                    "secret-tls": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog",
                    "tls": "enabled",
                    "resource": "orders",
                    "salt": "ATHqbN8tSre0HiFf",
                    "version": "v0",
                    "data": (
                        '{"resource": "orders", "salt": "ATHqbN8tSre0HiFf",'
                        ' "extra-user-roles": "consumer,producer",'
                        ' "requested-secrets": ["username", "password", "tls", "tls-ca", "uris"]}'
                    ),
                },
                {
                    "topic": "orders",
                    "endpoints": "10.141.78.155:9092,10.141.78.62:9092,10.141.78.186:9092",
                    "zookeeper-uris": "10.141.78.133:2181,10.141.78.50:2181,10.141.78.45:2181/kafka",
                    "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0",
                    "secret-tls": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog",
                    "data": (
                        '{"topic": "orders", "extra-user-roles": "admin",'
                        ' "requested-secrets": "[\\"username\\", \\"password\\", \\"tls\\", \\"tls-ca\\", \\"uris\\"]"}'
                    ),
                },
                {
                    "topic": "orders",
                    "endpoints": "10.141.78.155:9092",
                    "username": "relation-14",
                    "password": "Dy0k2UTfyNt2B13cfe412K7YGs07S4U7",
                    "consumer-group-prefix": "relation-14-",
                    "tls": "disabled",
                },
            ]
        },
    )

    topic: str = Field(
        description=(
            "The topic that the user has been granted access to. This might not be the topic"
            " that the requirer asked for."
        ),
        examples=["orders", "appname-*"],
        title="Topic name",
    )

    endpoints: str = Field(
        description="A comma-separated list of Kafka broker addresses, as `host:port`.",
        examples=["10.141.78.155:9092,10.141.78.62:9092,10.141.78.186:9092"],
        title="Kafka server endpoints",
    )

    username: str | None = Field(
        default=None,
        description=(
            "The SASL/SCRAM username for connecting to the Kafka cluster. Only in the databag"
            " when the requirer doesn't list it in `requested-secrets`; otherwise it's in the"
            " `secret-user` secret."
        ),
        examples=["relation-14"],
        title="Kafka SASL/SCRAM username",
    )

    password: str | None = Field(
        default=None,
        description=(
            "The SASL/SCRAM password for connecting to the Kafka cluster. Only in the databag"
            " when the requirer doesn't list it in `requested-secrets`; otherwise it's in the"
            " `secret-user` secret."
        ),
        examples=["Dy0k2UTfyNt2B13cfe412K7YGs07S4U7"],
        title="Kafka SASL/SCRAM password",
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
            "Whether the brokers' client listeners use TLS: `enabled` or `disabled`. In the"
            " `secret-tls` secret instead when the requirer lists it in `requested-secrets`"
            " and the provider uses the v0 library."
        ),
        examples=["enabled", "disabled"],
        title="TLS",
    )

    tls_ca: str | None = Field(
        default=None,
        alias="tls-ca",
        description=(
            "The CA certificate chain for the brokers' client listeners, as PEM. Only in the"
            " databag when the requirer doesn't list it in `requested-secrets`; otherwise it's"
            " in the `secret-tls` secret."
        ),
        examples=["-----BEGIN CERTIFICATE-----\nMIIC...\n-----END CERTIFICATE-----"],
        title="TLS CA",
    )

    secret_tls: str | None = Field(
        default=None,
        alias="secret-tls",
        description=(
            "The ID of a Juju secret with the TLS settings: `tls-ca` when TLS is enabled, and"
            " `tls` for providers that use the v0 library."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog"],
        title="TLS secret ID",
    )

    consumer_group_prefix: str | None = Field(
        default=None,
        alias="consumer-group-prefix",
        description=(
            "The prefix of the consumer group IDs that the user has been granted access to."
            " Set when `extra-user-roles` includes `consumer`."
        ),
        examples=["relation-14-"],
        title="Kafka consumer group prefix",
    )

    zookeeper_uris: str | None = Field(
        default=None,
        alias="zookeeper-uris",
        description=(
            "A comma-separated list of ZooKeeper server addresses, followed by the Kafka"
            " cluster's zNode. Only written by Kafka 3, which uses ZooKeeper."
        ),
        examples=["10.141.78.133:2181,10.141.78.50:2181,10.141.78.45:2181/kafka"],
        title="ZooKeeper URIs",
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

    resource: str | None = Field(
        default=None,
        description=(
            "A copy of `topic`, written by providers that use the v1 data_interfaces library."
        ),
        examples=["orders"],
        title="Resource",
    )

    salt: str | None = Field(
        default=None,
        description=(
            "A random string that the v1 data_interfaces library uses to identify the request."
        ),
        examples=["ATHqbN8tSre0HiFf"],
        title="Salt",
    )

    version: str | None = Field(
        default=None,
        description=(
            "The data_interfaces protocol version that the provider is answering with, written"
            " by providers that use the v1 data_interfaces library. Always `v0` for this"
            " interface."
        ),
        examples=["v0"],
        title="Protocol version",
    )

    data: dict[str, Any] | None = Field(
        default=None,
        description=(
            "The requirer's application databag as the provider last saw it, used by the"
            " library to work out what changed. A JSON object on the wire."
        ),
        examples=[{"topic": "orders", "extra-user-roles": "producer"}],
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
                    "topic": "orders",
                    "extra-user-roles": "consumer,producer",
                    "consumer-group-prefix": "orders-cg-",
                    "requested-secrets": (
                        '["username", "password", "tls", "tls-ca", "uris", "read-only-uris",'
                        ' "entity-name", "entity-password"]'
                    ),
                    "provided-secrets": '["mtls-cert"]',
                },
                {
                    "topic": "orders",
                    "extra-user-roles": "producer",
                    "requested-secrets": '["username", "password", "tls", "tls-ca", "uris"]',
                    "provided-secrets": '["mtls-cert"]',
                    "secret-mtls": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/d2qub7fubg2s77p3nk10",
                },
                {
                    "topic": "orders",
                    "entity-type": "USER",
                    "entity-permissions": (
                        '[{"resource_name": "orders", "resource_type": "TOPIC",'
                        ' "privileges": ["READ"]}]'
                    ),
                    "requested-secrets": (
                        '["username", "password", "tls", "tls-ca", "uris", "read-only-uris",'
                        ' "entity-name", "entity-password"]'
                    ),
                },
            ]
        },
    )

    topic: str = Field(
        description=(
            "The topic that the requirer wants access to. A name ending in `*` asks for every"
            " topic with that prefix. It must not have a `*` in its first three characters."
        ),
        examples=["orders", "appname-*"],
        title="Topic name",
    )

    extra_user_roles: str | None = Field(
        default=None,
        alias="extra-user-roles",
        description=(
            "A comma-separated list of the roles that the requirer wants: `producer`,"
            " `consumer`, `admin`, or `manager`."
        ),
        examples=["producer", "consumer", "consumer,producer", "admin", "manager"],
        title="Extra user roles",
    )

    consumer_group_prefix: str | None = Field(
        default=None,
        alias="consumer-group-prefix",
        description=(
            "The prefix of the consumer group IDs that the requirer wants access to, when"
            " `extra-user-roles` includes `consumer`."
        ),
        examples=["orders-cg-"],
        title="Kafka consumer group prefix",
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
            "The permissions that the requirer wants, as a JSON list of objects with"
            " `resource_name`, `resource_type` (`TOPIC` or `GROUP`), and `privileges`. The"
            " library writes this string as it's given."
        ),
        examples=[
            '[{"resource_name": "orders", "resource_type": "TOPIC", "privileges": ["READ"]}]'
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

    mtls_cert: str | None = Field(
        default=None,
        alias="mtls-cert",
        description=(
            "The requirer's client certificate, as PEM, for mutual TLS. Only in the databag"
            " when secrets aren't available; otherwise it's in the `secret-mtls` secret."
        ),
        examples=["-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----"],
        title="mTLS certificate",
    )

    secret_mtls: str | None = Field(
        default=None,
        alias="secret-mtls",
        description="The ID of a Juju secret with the `mtls-cert` key.",
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/d2qub7fubg2s77p3nk10"],
        title="mTLS secret ID",
    )

    @field_validator("extra_user_roles", mode="before")
    @classmethod
    def _check_roles(cls, value: Any) -> Any:
        if isinstance(value, str):
            valid = {role.value for role in ExtraUserRole}
            for role in value.split(","):
                if role.strip() not in valid:
                    raise ValueError(f"Role {role} is not valid.")
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
                        '{"topic": "orders", "endpoints": "10.141.78.155:9092",'
                        ' "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0",'
                        ' "consumer-group-prefix": "orders-cg-"}'
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
        examples=[{"topic": "orders", "endpoints": "10.141.78.155:9092"}],
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
