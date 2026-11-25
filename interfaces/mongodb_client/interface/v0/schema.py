"""This file defines the schemas for the provider and requirer sides of the mongodb_client interface."""

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


class ProviderAppData(_BareStringDatabag):
    """The databag for the provider side of this interface."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            'examples': [
                {
                    'database': 'myappB',
                    'endpoints': (
                        'mongodb-k8s-0.mongodb-k8s-endpoints,mongodb-k8s-1.mongodb-k8s-endpoints'
                    ),
                    'replset': 'mongodb-k8s',
                    'secret-user': (
                        'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0'
                    ),
                    'secret-tls': 'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog',
                },
                {
                    'database': 'myapp',
                    'endpoints': '10.180.162.5:27017',
                    'replset': 'mongodb',
                    'username': 'relation-4',
                    'password': 'Dy0k2UTfyNt2B13cfe412K7YGs07S4U7',
                    'uris': (
                        'mongodb://relation-4:Dy0k2UTfyNt2B13cfe412K7YGs07S4U7@10.180.162.5:27017'
                        '/myapp?replicaSet=mongodb&authSource=admin'
                    ),
                },
            ]
        },
    )

    database: str = Field(
        description=(
            'The database name delivered by the provider. Might not be the same as requested by'
            ' the requirer.'
        ),
        examples=['myapp'],
        title='Database name',
    )

    endpoints: str | None = Field(
        None,
        description=(
            'A comma-separated list of hosts that can be used to connect to the database. A'
            ' config server in a sharded cluster leaves it out.'
        ),
        examples=['10.180.162.5:27017,10.180.162.6:27017'],
        title='Database endpoints',
    )

    replset: str | None = Field(
        None,
        description=(
            'The name of the replica set, which is needed to connect to MongoDB when sharding is'
            ' disabled.'
        ),
        examples=['rs0'],
        title='Replica set',
    )

    version: str | None = Field(
        None,
        description='The version of the database engine.',
        examples=['8.0.27-18'],
        title='Version',
    )

    secret_user: str | None = Field(
        None,
        alias='secret-user',
        description=(
            'The ID of a Juju secret with the relation user credentials, under the `username`,'
            ' `password`, and `uris` keys.'
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
        examples=['relation-14'],
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
            'A connection string in URI format that can be passed to MongoDB client libraries as'
            ' it is, when it is not in a secret.'
        ),
        examples=[
            'mongodb://user:pass@host1:27017,host2:27017/myapp?replicaSet=rs0&authSource=admin'
        ],
        title='Database URI',
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
                    'requested-secrets': _REQUESTED_SECRETS_EXAMPLE,
                    'provided-secrets': '["mtls-cert"]',
                },
                {
                    'database': 'myapp',
                    'requested-secrets': _REQUESTED_SECRETS_EXAMPLE,
                    'provided-secrets': '["mtls-cert"]',
                    'extra-user-roles': 'admin',
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
        description='A comma-separated list of extra roles for the relation user.',
        examples=['admin', 'default,admin'],
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
            '[{"resource_name": "posts", "resource_type": "COLLECTION", "privileges": ["READ"]}]'
        ],
        title='Entity permissions',
    )

    external_node_connectivity: str | None = Field(
        None,
        alias='external-node-connectivity',
        description=(
            'Whether the requirer connects from outside the provider\'s network ("true" or'
            ' "false"). The provider only restricts where the relation user can connect from'
            ' when this is not "true".'
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
