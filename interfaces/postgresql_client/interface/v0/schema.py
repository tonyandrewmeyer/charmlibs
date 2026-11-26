"""This file defines the schemas for the provider and requirer sides of the postgresql_client interface."""

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
    return None if value is None else json.dumps(value)


_ALL_REQUESTED_SECRETS = [
    "username",
    "password",
    "tls",
    "tls-ca",
    "uris",
    "read-only-uris",
    "entity-name",
    "entity-password",
]
_CA = "-----BEGIN CERTIFICATE-----\nMIIDdzCCAl+gAwIBAgIUZ...\n-----END CERTIFICATE-----"


class ProviderAppData(_BareStringDatabag):
    """The databag for the provider side of this interface."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "database": "myappB",
                    "endpoints": "postgresql-k8s-primary.dev.svc.cluster.local:5432",
                    "read-only-endpoints": "postgresql-k8s-replicas.dev.svc.cluster.local:5432",
                    "version": "16.10",
                    "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0",
                    "secret-tls": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog",
                },
                {
                    "database": "myapp",
                    "endpoints": "10.180.162.5:5432",
                    "read-only-endpoints": "10.180.162.6:5432,10.180.162.7:5432",
                    "version": "14.19",
                    "username": "relation-17",
                    "password": "Dy0k2UTfyNt2B13cfe412K7YGs07S4U7",
                    "uris": "postgresql://relation-17:Dy0k2UTfyNt2B13cfe412K7YGs07S4U7@10.180.162.5:5432/myapp",
                    "tls": "True",
                    "tls-ca": _CA,
                },
                {
                    "database": "myapp*",
                    "prefix-databases": "myapp_orders,myapp_users",
                    "endpoints": "10.180.162.5:5432",
                    "read-only-endpoints": "10.180.162.6:5432,10.180.162.7:5432",
                    "version": "16.10",
                    "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub8fubg2s77p3nip0",
                    "secret-tls": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub9fubg2s77p3nipg",
                },
                {
                    "subordinated": "true",
                    "database": "myapp",
                    "endpoints": "/var/snap/charmed-pgbouncer/current/run/pgbouncer/pgbouncer/instance_0:6432",
                    "read-only-endpoints": "/var/snap/charmed-pgbouncer/current/run/pgbouncer/pgbouncer/instance_0:6432",
                    "version": "16.10",
                    "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqubafubg2s77p3niq0",
                },
            ]
        },
    )

    database: str = Field(
        description=(
            "The name of the database that the provider created, which might not be the one that"
            " the requirer asked for. For a prefix request, this is the requested prefix, ending"
            " in `*`."
        ),
        examples=["myapp", "myapp*"],
        title="Database name",
    )

    endpoints: str = Field(
        description=(
            "The address of the primary, as `host:port`, which can be used for read/write"
            " queries. PgBouncer on machines writes the path of its Unix socket directory as the"
            " host unless the requirer sets `external-node-connectivity`."
        ),
        examples=[
            "postgresql-k8s-primary.dev.svc.cluster.local:5432",
            "10.180.162.5:5432",
            "/var/snap/charmed-pgbouncer/current/run/pgbouncer/pgbouncer/instance_0:6432",
        ],
        title="Database endpoints",
    )

    read_only_endpoints: str | None = Field(
        None,
        alias="read-only-endpoints",
        description=(
            "A comma-separated list of `host:port` addresses, or one Kubernetes service, that can"
            " be used for read-only queries. When there are no replicas, this is the primary."
        ),
        examples=[
            "postgresql-k8s-replicas.dev.svc.cluster.local:5432",
            "10.180.162.6:5432,10.180.162.7:5432",
        ],
        title="Database read-only endpoints",
    )

    version: str | None = Field(
        None,
        description="The version of the database engine.",
        examples=["16.10", "14.19"],
        title="Version",
    )

    prefix_databases: str | None = Field(
        None,
        alias="prefix-databases",
        description=(
            "A comma-separated, sorted list of the databases that match a requested prefix. Not"
            " written when no database matches."
        ),
        examples=["myapp_orders,myapp_users"],
        title="Prefix databases",
    )

    subordinated: str | None = Field(
        None,
        description=(
            'Set to "true" by a subordinate provider, such as PgBouncer on machines, so that the'
            " requirer waits for each provider unit to set `state` before using it."
        ),
        examples=["true"],
        title="Subordinated",
    )

    secret_user: str | None = Field(
        None,
        alias="secret-user",
        description=(
            "The ID of a Juju secret with the relation user credentials, under the `username` and"
            " `password` keys, and `uris` and `read-only-uris` if the requirer listed them in"
            " `requested-secrets`."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0"],
        title="User secret ID",
    )

    secret_tls: str | None = Field(
        None,
        alias="secret-tls",
        description=(
            "The ID of a Juju secret with whichever of `tls` and `tls-ca` the requirer listed in"
            " `requested-secrets`."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog"],
        title="TLS secret ID",
    )

    secret_extra: str | None = Field(
        None,
        alias="secret-extra",
        description=(
            "The ID of a Juju secret with any other fields that the requirer listed in"
            " `requested-secrets`."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqubbfubg2s77p3niqg"],
        title="Extra secret ID",
    )

    username: str | None = Field(
        None,
        description="The username for connecting to the requested database, when it is not in a secret.",
        examples=["relation-17"],
        title="Database user name",
    )

    password: str | None = Field(
        None,
        description="The password for connecting to the requested database, when it is not in a secret.",
        examples=["Dy0k2UTfyNt2B13cfe412K7YGs07S4U7"],
        title="Database user password",
    )

    uris: str | None = Field(
        None,
        description=(
            "A connection string for the primary, in libpq's URI format, when it is not in a"
            " secret. Not written for a prefix request that no database matches."
        ),
        examples=[
            "postgresql://relation-17:Dy0k2UTfyNt2B13cfe412K7YGs07S4U7@10.180.162.5:5432/myapp"
        ],
        title="Database URIs",
    )

    read_only_uris: str | None = Field(
        None,
        alias="read-only-uris",
        description=(
            "A connection string for the read-only endpoints, in libpq's URI format. Only written"
            " when the requirer lists it in `requested-secrets`, so it is normally in the user"
            " secret rather than in the databag."
        ),
        examples=[
            "postgresql://relation-17:Dy0k2UTfyNt2B13cfe412K7YGs07S4U7@10.180.162.6,10.180.162.7:5432/myapp"
        ],
        title="Database read-only URIs",
    )

    tls: str | None = Field(
        None,
        description='Whether TLS is enabled ("True" or "False"), when it is not in a secret.',
        examples=["True", "False"],
        title="TLS enabled",
    )

    tls_ca: str | None = Field(
        None,
        alias="tls-ca",
        description=(
            "The CA chain, in PEM format, when TLS is enabled and it is not in a secret. When TLS"
            " is disabled, the provider writes an empty string, which removes the field."
        ),
        examples=[_CA],
        title="TLS CA chain",
    )

    data: dict[str, str] | None = Field(
        None,
        description=(
            "A JSON copy of the requirer's application databag, which the library keeps to work"
            " out what has changed. A JSON object on the wire."
        ),
        examples=[{"database": "myapp", "requested-secrets": '["username", "password"]'}],
        title="Requirer data copy",
    )

    @field_validator("data", mode="before")
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        return _load_json(value)

    @field_serializer("data")
    def _dump_json(self, value: object) -> str | None:
        return _dump_json(value)


class ProviderUnitData(_BareStringDatabag):
    """The databag for each provider unit. Only subordinate providers write to it."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={"examples": [{"state": "ready"}]},
    )

    state: str | None = Field(
        None,
        description=(
            'Set to "ready" by each unit of a subordinate provider once it can serve. When the'
            ' provider sets `subordinated`, the requirer waits for this.'
        ),
        examples=["ready"],
        title="State",
    )


class RequirerAppData(_BareStringDatabag):
    """The databag for the requirer side of this interface."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "database": "myappA",
                    "requested-secrets": '["username", "password", "tls-ca", "uris"]',
                },
                {
                    "database": "pgbouncer",
                    "extra-user-roles": "SUPERUSER",
                    "requested-secrets": json.dumps(_ALL_REQUESTED_SECRETS),
                    "provided-secrets": '["mtls-cert"]',
                },
                {
                    "database": "myapp",
                    "extra-user-roles": "charmed_dml",
                    "external-node-connectivity": "true",
                    "requested-entity-secret": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/d2fjn1fmp25004or68b0",
                    "requested-secrets": json.dumps(_ALL_REQUESTED_SECRETS),
                    "provided-secrets": '["mtls-cert"]',
                },
                {
                    "database": "myapp*",
                    "prefix-matching": "all",
                    "requested-secrets": json.dumps(_ALL_REQUESTED_SECRETS),
                    "provided-secrets": '["mtls-cert"]',
                },
            ]
        },
    )

    database: str = Field(
        description=(
            "The name of the database that the requirer wants, or a prefix: at least three"
            " characters followed by `*`."
        ),
        examples=["myapp", "myapp*"],
        title="Database name",
    )

    requested_secrets: list[str] = Field(
        alias="requested-secrets",
        description=(
            "The provider fields that should be sent in Juju secrets rather than in the databag."
            " A JSON array on the wire."
        ),
        examples=[_ALL_REQUESTED_SECRETS],
        title="Requested secrets",
    )

    provided_secrets: list[str] | None = Field(
        None,
        alias="provided-secrets",
        description="The requirer fields that the requirer sends in Juju secrets. A JSON array on the wire.",
        examples=[["mtls-cert"]],
        title="Provided secrets",
    )

    extra_user_roles: str | None = Field(
        None,
        alias="extra-user-roles",
        description="A comma-separated list of extra roles or privileges for the relation user.",
        examples=["charmed_dml", "SUPERUSER", "createdb,charmed_read"],
        title="Extra user roles",
    )

    extra_group_roles: str | None = Field(
        None,
        alias="extra-group-roles",
        description="A comma-separated list of extra roles for the requested group.",
        examples=["charmed_read"],
        title="Extra group roles",
    )

    prefix_matching: str | None = Field(
        None,
        alias="prefix-matching",
        description="How to match databases against a requested prefix. The PostgreSQL charms only support `all`.",
        examples=["all"],
        title="Prefix matching",
    )

    entity_type: str | None = Field(
        None,
        alias="entity-type",
        description="The type of custom entity to create instead of a relation user.",
        examples=["USER", "GROUP"],
        title="Entity type",
    )

    entity_permissions: str | None = Field(
        None,
        alias="entity-permissions",
        description="A JSON list of permissions to assign to the custom entity.",
        examples=[
            '[{"resource_name": "items", "resource_type": "TABLE", "privileges": ["SELECT"]}]'
        ],
        title="Entity permissions",
    )

    requested_entity_secret: str | None = Field(
        None,
        alias="requested-entity-secret",
        description=(
            "The ID of a Juju secret with the name (under `entity-name`) and optionally the"
            " password (under `password`) that the requirer wants for its user."
        ),
        examples=["secret://59060ecc-0495-4a80-8006-5f1fc13fd783/d2fjn1fmp25004or68b0"],
        title="Requested entity secret ID",
    )

    external_node_connectivity: str | None = Field(
        None,
        alias="external-node-connectivity",
        description=(
            "Set to \"true\" when the requirer connects from outside the provider's host, so a"
            " subordinate provider exposes a network endpoint rather than a local one."
        ),
        examples=["true"],
        title="External node connectivity",
    )

    alias: str | None = Field(
        None,
        description="The alias that the requirer gave this relation.",
        examples=["cluster1"],
        title="Relation alias",
    )

    @field_validator("requested_secrets", "provided_secrets", mode="before")
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        return _load_json(value)

    @field_serializer("requested_secrets", "provided_secrets")
    def _dump_json(self, value: object) -> str | None:
        return _dump_json(value)


class RequirerUnitData(_BareStringDatabag):
    """The databag for each requirer unit, which the library uses for its own bookkeeping."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "requested-secrets": json.dumps(_ALL_REQUESTED_SECRETS),
                    "provided-secrets": '["mtls-cert"]',
                    "data": json.dumps({
                        "database": "myapp",
                        "endpoints": "10.180.162.5:5432",
                        "secret-user": "secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0",
                    }),
                },
                {
                    "requested-secrets": json.dumps(_ALL_REQUESTED_SECRETS),
                    "provided-secrets": '["mtls-cert"]',
                    "alias": "cluster1",
                },
            ]
        },
    )

    requested_secrets: list[str] | None = Field(
        None,
        alias="requested-secrets",
        description="A copy of `requested-secrets` from the application databag. A JSON array on the wire.",
        examples=[_ALL_REQUESTED_SECRETS],
        title="Requested secrets",
    )

    provided_secrets: list[str] | None = Field(
        None,
        alias="provided-secrets",
        description="A copy of `provided-secrets` from the application databag. A JSON array on the wire.",
        examples=[["mtls-cert"]],
        title="Provided secrets",
    )

    alias: str | None = Field(
        None,
        description="The alias that the requirer gave this relation.",
        examples=["cluster1"],
        title="Relation alias",
    )

    data: dict[str, str] | None = Field(
        None,
        description=(
            "A JSON copy of the provider's application databag, which the library keeps to work"
            " out what has changed. A JSON object on the wire."
        ),
        examples=[{"database": "myapp", "endpoints": "10.180.162.5:5432"}],
        title="Provider data copy",
    )

    @field_validator("requested_secrets", "provided_secrets", "data", mode="before")
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        return _load_json(value)

    @field_serializer("requested_secrets", "provided_secrets", "data")
    def _dump_json(self, value: object) -> str | None:
        return _dump_json(value)
