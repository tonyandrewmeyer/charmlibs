"""This file defines the schemas for the provider and requirer sides of the opensearch_client interface."""

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
                    'index': 'myindex',
                    'endpoints': '10.180.162.200:9200,10.180.162.75:9200',
                    'version': '2.19.2',
                    'secret-user': 'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0',
                    'secret-tls': 'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog',
                },
                {
                    'index': 'myindex',
                    'endpoints': '10.180.162.200:9200',
                    'version': '2.19.2',
                    'secret-entity': 'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub8fubg2s77p3nip0',
                    'secret-tls': 'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog',
                },
            ]
        },
    )

    index: str = Field(
        description=(
            'The index that has been made available to the relation user. Usually the index that'
            ' the requirer asked for in its `index` field.'
        ),
        examples=['myindex'],
        title='Index name',
    )

    endpoints: str | None = Field(
        None,
        description='A comma-separated list of the cluster endpoint addresses.',
        examples=['10.180.162.200:9200,10.180.162.75:9200'],
        title='Endpoints',
    )

    version: str | None = Field(
        None,
        description='The version of OpenSearch.',
        examples=['2.19.2'],
        title='Version',
    )

    secret_user: str | None = Field(
        None,
        alias='secret-user',
        description=(
            'The ID of a Juju secret with the relation user credentials, under the `username` and'
            ' `password` keys.'
        ),
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0'],
        title='User secret ID',
    )

    secret_tls: str | None = Field(
        None,
        alias='secret-tls',
        description='The ID of a Juju secret with the CA chain under the `tls-ca` key.',
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub7fubg2s77p3niog'],
        title='TLS secret ID',
    )

    secret_entity: str | None = Field(
        None,
        alias='secret-entity',
        description=(
            'The ID of a Juju secret with the custom entity details, under the `entity-name` key'
            ' (and `entity-password`, if there is one).'
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
        description='The username for connecting to the index, when it is not in a secret.',
        examples=['opensearch-client_4'],
        title='Relation user name',
    )

    password: str | None = Field(
        None,
        description='The password for connecting to the index, when it is not in a secret.',
        examples=['Dy0k2UTfyNt2B13cfe412K7YGs07S4U7'],
        title='Relation user password',
    )

    tls_ca: str | None = Field(
        None,
        alias='tls-ca',
        description='The CA chain, in PEM format, when it is not in a secret.',
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
        examples=['{"index": "myindex", "requested-secrets": "[\\"username\\", \\"password\\"]"}'],
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
                    'index': 'myindex',
                    'requested-secrets': _REQUESTED_SECRETS_EXAMPLE,
                    'provided-secrets': '["mtls-cert"]',
                },
                {
                    'index': 'myindex',
                    'requested-secrets': _REQUESTED_SECRETS_EXAMPLE,
                    'provided-secrets': '["mtls-cert"]',
                    'extra-group-roles': 'readall',
                    'entity-type': 'GROUP',
                    'requested-entity-secret': (
                        'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqubbfubg2s77p3niqg'
                    ),
                },
            ]
        },
    )

    index: str = Field(
        description='The index name requested by the requirer.',
        examples=['myindex'],
        title='Index name',
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
        'default',
        alias='extra-user-roles',
        description=(
            'A comma-separated list of roles for the relation user: `default` (read and write on'
            ' the index) or `admin` (control over the cluster). OpenSearch also accepts'
            ' `kibana_server`, for OpenSearch Dashboards.'
        ),
        examples=['default', 'admin'],
        title='Extra user roles',
    )

    extra_group_roles: str | None = Field(
        None,
        alias='extra-group-roles',
        description='A comma-separated list of extra roles for the requested group.',
        examples=['readall'],
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
            '[{"resource_name": "myindex", "resource_type": "INDEX", "privileges": ["WRITE"]}]'
        ],
        title='Entity permissions',
    )

    requested_entity_secret: str | None = Field(
        None,
        alias='requested-entity-secret',
        description=(
            'The ID of a Juju secret with the name the requirer wants for the custom entity, under'
            ' the `entity-name` key, and optionally a `password`. In a cross-model relation, the'
            ' encrypted name and password instead.'
        ),
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqubbfubg2s77p3niqg'],
        title='Requested entity secret ID',
    )

    encryption_secret: str | None = Field(
        None,
        alias='encryption-secret',
        description=(
            "A copy of the provider's `encryption-secret`, which the requirer writes in a"
            ' cross-model relation.'
        ),
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqubafubg2s77p3niq0'],
        title='Encryption secret ID',
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

    @field_validator('requested_secrets', 'provided_secrets', mode='before')
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        return _load_json_list(value)

    @field_serializer('requested_secrets', 'provided_secrets')
    def _dump_json(self, value: object) -> str | None:
        return None if value is None else json.dumps(value)


ProviderUnitData = None
