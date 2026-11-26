"""This file defines the schemas for the provider and requirer sides of the mysql_client interface."""

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
        return '' if value is None else value


class ProviderAppData(_BareStringDatabag):
    """The databag for the provider side of this interface."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            'examples': [
                {
                    'database': 'myappB',
                    'endpoints': 'mysql-k8s-primary:3306',
                    'read-only-endpoints': 'mysql-k8s-replicas:3306',
                    'version': '8.0.41-0ubuntu0.22.04.1',
                    'secret-user': (
                        'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0'
                    ),
                },
                {
                    'database': 'myapp',
                    'endpoints': '10.180.162.5:3306',
                    'read-only-endpoints': '10.180.162.6:3306,10.180.162.7:3306',
                    'version': '8.0.41-0ubuntu0.22.04.1',
                    'username': 'relation-4_59060ecc04954a8',
                    'password': 'Dy0k2UTfyNt2B13cfe412K7YGs07S4U7',
                },
                {
                    'endpoints': 'mysql-k8s-primary:3306',
                    'read-only-endpoints': 'mysql-k8s-replicas:3306',
                    'version': '8.0.41-0ubuntu0.22.04.1',
                    'secret-user': (
                        'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog'
                    ),
                },
                {
                    'database': 'myapp',
                    'endpoints': 'file:///var/snap/charmed-mysql/common/run/mysqlrouter/mysql.sock',
                    'read-only-endpoints': (
                        'file:///var/snap/charmed-mysql/common/run/mysqlrouter/mysqlro.sock'
                    ),
                    'secret-user': (
                        'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub8fubg2s77p3nip0'
                    ),
                },
            ]
        },
    )

    database: str | None = Field(
        None,
        description=(
            'The database name delivered by the provider. Might not be the same as requested by'
            ' the requirer. Not written when the requirer asks for the `charmed_router` role.'
        ),
        examples=['myapp'],
        title='Database name',
    )

    endpoints: str = Field(
        description=(
            'The address of the primary, which can be used for read/write queries. This is'
            ' `host:port`, except that MySQL Router on machines writes a `file://` URL for a Unix'
            ' socket unless the requirer sets `external-node-connectivity`.'
        ),
        examples=[
            'mysql-k8s-primary:3306',
            '10.180.162.5:3306',
            'file:///var/snap/charmed-mysql/common/run/mysqlrouter/mysql.sock',
        ],
        title='Database endpoints',
    )

    read_only_endpoints: str | None = Field(
        None,
        alias='read-only-endpoints',
        description=(
            'A comma-separated list of `host:port` addresses, or one Kubernetes service, that can'
            ' be used for read-only queries. MySQL Router on machines writes a `file://` URL for a'
            ' Unix socket unless the requirer sets `external-node-connectivity`.'
        ),
        examples=[
            'mysql-k8s-replicas:3306',
            '10.180.162.6:3306,10.180.162.7:3306',
            'file:///var/snap/charmed-mysql/common/run/mysqlrouter/mysqlro.sock',
        ],
        title='Database read-only endpoints',
    )

    version: str | None = Field(
        None,
        description='The version of the database engine.',
        examples=['8.0.41-0ubuntu0.22.04.1'],
        title='Version',
    )

    secret_user: str | None = Field(
        None,
        alias='secret-user',
        description=(
            'The ID of a Juju secret with the relation user credentials, under the `username` and'
            ' `password` keys, and `uris` and `read-only-uris` if the provider writes them and the'
            ' requirer listed them in `requested-secrets`.'
        ),
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0'],
        title='User secret ID',
    )

    secret_tls: str | None = Field(
        None,
        alias='secret-tls',
        description=(
            'The ID of a Juju secret with the TLS details, under the `tls` and `tls-ca` keys, when'
            ' TLS is enabled.'
        ),
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog'],
        title='TLS secret ID',
    )

    secret_entity: str | None = Field(
        None,
        alias='secret-entity',
        description=(
            'The ID of a Juju secret with the custom entity credentials, under the `entity-name`'
            ' and `entity-password` keys.'
        ),
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub8fubg2s77p3nip0'],
        title='Entity secret ID',
    )

    secret_extra: str | None = Field(
        None,
        alias='secret-extra',
        description=(
            'The ID of a Juju secret with any other fields that the requirer listed in'
            ' `requested-secrets`.'
        ),
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub9fubg2s77p3nipg'],
        title='Extra secret ID',
    )

    username: str | None = Field(
        None,
        description=(
            'The username for connecting to the requested database, when it is not in a secret.'
        ),
        examples=['relation-4_59060ecc04954a8'],
        title='Database user name',
    )

    password: str | None = Field(
        None,
        description=(
            'The password for connecting to the requested database, when it is not in a secret.'
        ),
        examples=['Dy0k2UTfyNt2B13cfe412K7YGs07S4U7'],
        title='Database user password',
    )

    uris: str | None = Field(
        None,
        description=(
            'A connection string for the primary, in MySQL Shell URI format, when it is not in a'
            ' secret.'
        ),
        examples=['mysql://relation-4:pass@mysql-k8s-primary:3306/myapp'],
        title='Database URIs',
    )

    read_only_uris: str | None = Field(
        None,
        alias='read-only-uris',
        description=(
            'A connection string for the read-only endpoint, in MySQL Shell URI format, when it is'
            ' not in a secret.'
        ),
        examples=['mysql://relation-4:pass@mysql-k8s-replicas:3306/myapp'],
        title='Database read-only URIs',
    )

    tls: str | None = Field(
        None,
        description='Whether TLS is enabled ("True" or "False"), when it is not in a secret.',
        examples=['True'],
        title='TLS enabled',
    )

    tls_ca: str | None = Field(
        None,
        alias='tls-ca',
        description='The CA chain, in PEM format, when TLS is enabled and it is not in a secret.',
        examples=[
            '-----BEGIN CERTIFICATE-----\nMIIDdzCCAl+gAwIBAgIUZ...\n-----END CERTIFICATE-----'
        ],
        title='TLS CA chain',
    )

    entity_name: str | None = Field(
        None,
        alias='entity-name',
        description='The name of the requested custom entity, when it is not in a secret.',
        examples=['custom-role'],
        title='Entity name',
    )

    entity_password: str | None = Field(
        None,
        alias='entity-password',
        description='The password of the requested custom entity, when it is not in a secret.',
        examples=['Dy0k2UTfyNt2B13cfe412K7YGs07S4U7'],
        title='Entity password',
    )

    encryption_secret: str | None = Field(
        None,
        alias='encryption-secret',
        description=(
            'The ID of a Juju secret with an `encryption-key` that the requirer uses to encrypt'
            ' sensitive fields, in a cross-model relation.'
        ),
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqubafubg2s77p3niq0'],
        title='Encryption secret ID',
    )

    data: str | None = Field(
        None,
        description=(
            "A JSON copy of the requirer's application databag, which the provider keeps to work"
            ' out what has changed.'
        ),
        examples=[
            '{"database": "myapp", "requested-secrets": "[\\"username\\", \\"password\\"]"}'
        ],
        title='Requirer data copy',
    )


def _load_json_list(value: Any) -> Any:
    if not isinstance(value, str):
        return value  # __init__ argument was already deserialized.
    return json.loads(value)


_REQUESTED_SECRETS_EXAMPLE = (
    '["username", "password", "tls", "tls-ca", "uris", "read-only-uris", "entity-name",'
    ' "entity-password"]'
)


class RequirerAppData(_BareStringDatabag):
    """The databag for the requirer side of this interface."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            'examples': [
                {
                    'database': 'myappA',
                    'requested-secrets': '["username", "password", "tls-ca", "uris"]',
                },
                {
                    'database': 'mysql_innodb_cluster_metadata',
                    'extra-user-roles': 'charmed_router',
                    'requested-secrets': '["username", "password", "tls", "tls-ca", "uris"]',
                },
                {
                    'database': 'myapp',
                    'requested-secrets': _REQUESTED_SECRETS_EXAMPLE,
                    'provided-secrets': '["mtls-cert"]',
                    'external-node-connectivity': 'true',
                },
            ]
        },
    )

    database: str = Field(
        description='The database name requested by the requirer.',
        examples=['myapp'],
        title='Database name',
    )

    requested_secrets: list[str] = Field(
        alias='requested-secrets',
        description=(
            'The provider fields that should be sent in Juju secrets rather than in the databag.'
            ' A JSON array on the wire.'
        ),
        examples=[['username', 'password', 'tls', 'tls-ca', 'uris']],
        title='Requested secrets',
    )

    provided_secrets: list[str] | None = Field(
        None,
        alias='provided-secrets',
        description=(
            'The requirer fields that the requirer sends in Juju secrets. A JSON array on the'
            ' wire.'
        ),
        examples=[['mtls-cert']],
        title='Provided secrets',
    )

    extra_user_roles: str | None = Field(
        None,
        alias='extra-user-roles',
        description=(
            'A comma-separated list of extra roles for the relation user. MySQL Router asks for'
            ' `charmed_router`.'
        ),
        examples=['charmed_dml', 'charmed_router'],
        title='Extra user roles',
    )

    extra_group_roles: str | None = Field(
        None,
        alias='extra-group-roles',
        description='A comma-separated list of extra roles for the requested group.',
        examples=['charmed_read'],
        title='Extra group roles',
    )

    entity_type: str | None = Field(
        None,
        alias='entity-type',
        description='The type of custom entity to create instead of a relation user.',
        examples=['USER', 'GROUP'],
        title='Entity type',
    )

    entity_permissions: str | None = Field(
        None,
        alias='entity-permissions',
        description='A JSON list of permissions to assign to the custom entity.',
        examples=[
            '[{"resource_name": "items", "resource_type": "TABLE", "privileges": ["SELECT"]}]'
        ],
        title='Entity permissions',
    )

    requested_entity_secret: str | None = Field(
        None,
        alias='requested-entity-secret',
        description=(
            'The ID of a Juju secret with the name (under `entity-name`) and optionally the'
            ' password (under `password`) that the requirer wants for the custom entity.'
        ),
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqubbfubg2s77p3niqg'],
        title='Requested entity secret ID',
    )

    external_node_connectivity: str | None = Field(
        None,
        alias='external-node-connectivity',
        description=(
            'Whether the requirer connects from outside the provider\'s network ("true" or'
            ' "false").'
        ),
        examples=['true'],
        title='External node connectivity',
    )

    alias: str | None = Field(
        None,
        description='The alias that the requirer gave this relation.',
        examples=['cluster1'],
        title='Relation alias',
    )

    @field_validator('requested_secrets', 'provided_secrets', mode='before')
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        return _load_json_list(value)

    @field_serializer('requested_secrets', 'provided_secrets')
    def _dump_json(self, value: object) -> str | None:
        return None if value is None else json.dumps(value)


class RequirerUnitData(_BareStringDatabag):
    """The databag for each requirer unit. The library writes copies of the secret field lists."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            'examples': [
                {
                    'requested-secrets': _REQUESTED_SECRETS_EXAMPLE,
                    'provided-secrets': '["mtls-cert"]',
                },
            ]
        },
    )

    requested_secrets: list[str] | None = Field(
        None,
        alias='requested-secrets',
        description='A copy of `requested-secrets` from the application databag.',
        examples=[['username', 'password', 'tls', 'tls-ca', 'uris']],
        title='Requested secrets',
    )

    provided_secrets: list[str] | None = Field(
        None,
        alias='provided-secrets',
        description='A copy of `provided-secrets` from the application databag.',
        examples=[['mtls-cert']],
        title='Provided secrets',
    )

    alias: str | None = Field(
        None,
        description='The alias that the requirer gave this relation.',
        examples=['cluster1'],
        title='Relation alias',
    )

    @field_validator('requested_secrets', 'provided_secrets', mode='before')
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        return _load_json_list(value)

    @field_serializer('requested_secrets', 'provided_secrets')
    def _dump_json(self, value: object) -> str | None:
        return None if value is None else json.dumps(value)


ProviderUnitData = None
