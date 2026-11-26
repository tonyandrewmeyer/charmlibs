# Copyright 2026 Canonical
# See LICENSE file for licensing details.

"""The v1 data contract of `dpcharmlibs.interfaces`, as Valkey uses it.

Both sides write `version` and a JSON array of requests (requirer) or responses (provider) in
`requests`. Unset values in the array are written as JSON `null`.
"""

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


_EXAMPLE_URI = 'secret://bc7400b7-2fce-41dd-8509-14a984455cda/d7fmpmvmp25c7618tfb0'


class EntityPermission(BaseModel):
    """A permission for a custom entity."""

    model_config = ConfigDict(strict=True)

    resource_name: str = Field(
        description='The name of the resource that the permission applies to.',
        examples=['app:*'],
        title='Resource name',
    )
    resource_type: str = Field(
        description='The type of the resource.',
        examples=['KEY'],
        title='Resource type',
    )
    privileges: list[str] = Field(
        description='The privileges to grant on the resource.',
        examples=[['READ', 'WRITE']],
        title='Privileges',
    )


class Request(BaseModel):
    """A request for access to a range of keys."""

    model_config = ConfigDict(strict=True, populate_by_name=True)

    resource: str = Field(
        description=(
            'The keys and Pub/Sub channels that the requirer wants to access, as a glob pattern.'
        ),
        examples=['app:*', '*'],
        title='Resource',
    )
    request_id: str = Field(
        alias='request-id',
        description=(
            'An ID for the request: the first 16 characters of the SHA-256 hash of'
            ' `<resource>:<salt>`.'
        ),
        examples=['836763deea236532'],
        title='Request ID',
    )
    salt: str = Field(
        description='A random string, which makes the request ID unique.',
        examples=['xqbPuYzzl2iiKeyN'],
        title='Salt',
    )
    extra_user_roles: str | None = Field(
        None,
        alias='extra-user-roles',
        description='A comma-separated list of extra roles for the user.',
        examples=['admin'],
        title='Extra user roles',
    )
    extra_group_roles: str | None = Field(
        None,
        alias='extra-group-roles',
        description='A comma-separated list of extra roles for the requested group.',
        examples=['readonly'],
        title='Extra group roles',
    )
    external_node_connectivity: bool | None = Field(
        None,
        alias='external-node-connectivity',
        description="Whether the requirer connects from outside the provider's network.",
        examples=[False],
        title='External node connectivity',
    )
    entity_type: str | None = Field(
        None,
        alias='entity-type',
        description='The type of custom entity to create instead of a user.',
        examples=['GROUP'],
        title='Entity type',
    )
    entity_permissions: list[EntityPermission] | None = Field(
        None,
        alias='entity-permissions',
        description='The permissions to assign to the custom entity.',
        examples=[[{'resource_name': 'app:*', 'resource_type': 'KEY', 'privileges': ['READ']}]],
        title='Entity permissions',
    )
    secret_mtls: str | None = Field(
        None,
        alias='secret-mtls',
        description=(
            'The ID of a Juju secret with a client certificate under the `mtls-cert` key. Valkey'
            ' doesn\'t use it.'
        ),
        examples=[_EXAMPLE_URI],
        title='mTLS secret ID',
    )
    mtls_cert: str | None = Field(
        None,
        alias='mtls-cert',
        description='The encrypted client certificate, in a cross-model relation.',
        examples=['gAAAAABpZ3J5cHRlZC1jZXJ0aWZpY2F0ZQ=='],
        title='mTLS certificate',
    )
    secret_requested_entity: str | None = Field(
        None,
        alias='secret-requested-entity',
        description=(
            'The ID of a Juju secret with the name and password the requirer wants for the'
            ' custom entity.'
        ),
        examples=[_EXAMPLE_URI],
        title='Requested entity secret ID',
    )
    entity_name: str | None = Field(
        None,
        alias='entity-name',
        description='The encrypted name of the requested entity, in a cross-model relation.',
        examples=['gAAAAABpZW50aXR5LW5hbWU='],
        title='Entity name',
    )
    entity_password: str | None = Field(
        None,
        alias='entity-password',
        description='The encrypted password of the requested entity, in a cross-model relation.',
        examples=['gAAAAABpZW50aXR5LXBhc3N3b3Jk'],
        title='Entity password',
    )
    password: str | None = Field(
        None,
        description='The encrypted password the requirer wants, in a cross-model relation.',
        examples=['gAAAAABpcGFzc3dvcmQ='],
        title='Password',
    )
    prefix_matching: str | None = Field(
        None,
        alias='prefix-matching',
        description='How to match the resource as a prefix, if the provider supports it.',
        examples=['all'],
        title='Prefix matching',
    )


class Response(BaseModel):
    """The provider's response to a request."""

    model_config = ConfigDict(strict=True, populate_by_name=True)

    resource: str = Field(
        description='The `resource` from the request.',
        examples=['app:*'],
        title='Resource',
    )
    request_id: str = Field(
        alias='request-id',
        description='The `request-id` of the request that this responds to.',
        examples=['836763deea236532'],
        title='Request ID',
    )
    salt: str = Field(
        description='The `salt` from the request.',
        examples=['xqbPuYzzl2iiKeyN'],
        title='Salt',
    )
    endpoints: str = Field(
        description='A comma-separated list of the Valkey read-write endpoints.',
        examples=['valkey-1.valkey-endpoints:6379'],
        title='Endpoints',
    )
    read_only_endpoints: str = Field(
        alias='read-only-endpoints',
        description='A comma-separated list of the Valkey read-only endpoints.',
        examples=['valkey-0.valkey-endpoints:6379,valkey-2.valkey-endpoints:6379'],
        title='Read-only endpoints',
    )
    sentinel_endpoints: str | None = Field(
        None,
        alias='sentinel-endpoints',
        description='A comma-separated list of the Valkey Sentinel endpoints, if available.',
        examples=[
            'valkey-0.valkey-endpoints:26379,valkey-1.valkey-endpoints:26379,'
            'valkey-2.valkey-endpoints:26379'
        ],
        title='Sentinel endpoints',
    )
    mode: str = Field(
        description='The high availability mode of Valkey. Currently always `sentinel`.',
        examples=['sentinel'],
        title='High availability mode',
    )
    version: str = Field(
        description='The version of Valkey.',
        examples=['9.0.1'],
        title='Valkey version',
    )
    secret_user: str = Field(
        alias='secret-user',
        description=(
            'The ID of a Juju secret with the credentials of the user created for this request,'
            ' under the `username` and `password` keys.'
        ),
        examples=[_EXAMPLE_URI],
        title='User secret ID',
    )
    secret_tls: str = Field(
        alias='secret-tls',
        description=(
            'The ID of a Juju secret with whether TLS is enabled (`true` or `false`) under the'
            ' `tls` key, and the CA certificate of the server under the `tls-ca` key when it is.'
        ),
        examples=['secret://bc7400b7-2fce-41dd-8509-14a984455cda/d7fmpmvmp25c7618tfbg'],
        title='TLS secret ID',
    )
    secret_extra: str | None = Field(
        None,
        alias='secret-extra',
        description='The ID of a Juju secret with any other sensitive fields. Valkey doesn\'t use it.',
        examples=[_EXAMPLE_URI],
        title='Extra secret ID',
    )
    secret_entity: str | None = Field(
        None,
        alias='secret-entity',
        description=(
            'The ID of a Juju secret with the custom entity credentials. Valkey doesn\'t use it.'
        ),
        examples=[_EXAMPLE_URI],
        title='Entity secret ID',
    )
    prefix_resources: str | None = Field(
        None,
        alias='prefix-resources',
        description='The resources that match a prefix request. Valkey doesn\'t use it.',
        examples=['app:a,app:b'],
        title='Prefix resources',
    )
    mtls_cert: str | None = Field(
        None,
        alias='mtls-cert',
        description='Unused by Valkey, which always writes `null`.',
        examples=[None],
        title='mTLS certificate',
    )
    entity_name: str | None = Field(
        None,
        alias='entity-name',
        description='Unused by Valkey, which always writes `null`.',
        examples=[None],
        title='Entity name',
    )
    entity_password: str | None = Field(
        None,
        alias='entity-password',
        description='Unused by Valkey, which always writes `null`.',
        examples=[None],
        title='Entity password',
    )
    password: str | None = Field(
        None,
        description='Unused by Valkey, which always writes `null`; the password is in the user secret.',
        examples=[None],
        title='Password',
    )


def _load_json(value: Any) -> Any:
    if not isinstance(value, str):
        return value  # __init__ argument was already deserialized.
    return json.loads(value)


_REQUIRER_REQUESTS = json.dumps([
    {
        'resource': 'app:*',
        'request-id': 'a0e66a95ec879066',
        'salt': 'SALTSALTSALTSALT',
        'extra-user-roles': None,
        'extra-group-roles': None,
        'external-node-connectivity': False,
        'entity-type': None,
        'entity-permissions': None,
        'secret-mtls': None,
        'mtls-cert': None,
        'secret-requested-entity': None,
        'entity-name': None,
        'password': None,
        'prefix-matching': None,
        'entity-password': None,
    }
])

_PROVIDER_REQUESTS = json.dumps([
    {
        'resource': 'app:*',
        'request-id': 'a0e66a95ec879066',
        'salt': 'SALTSALTSALTSALT',
        'endpoints': 'valkey-1.valkey-endpoints:6379',
        'read-only-endpoints': 'valkey-0.valkey-endpoints:6379,valkey-2.valkey-endpoints:6379',
        'secret-user': 'secret://bc7400b7-2fce-41dd-8509-14a984455cda/d7fmpmvmp25c7618tfb0',
        'secret-tls': 'secret://bc7400b7-2fce-41dd-8509-14a984455cda/d7fmpmvmp25c7618tfbg',
        'secret-extra': None,
        'secret-entity': None,
        'version': '9.0.1',
        'prefix-resources': None,
        'sentinel-endpoints': (
            'valkey-0.valkey-endpoints:26379,valkey-1.valkey-endpoints:26379,'
            'valkey-2.valkey-endpoints:26379'
        ),
        'mode': 'sentinel',
        'mtls-cert': None,
        'entity-name': None,
        'entity-password': None,
        'password': None,
    }
])


class ProviderAppData(_BareStringDatabag):
    """The provider's application databag."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={'examples': [{'version': 'v1', 'requests': _PROVIDER_REQUESTS}]},
    )

    version: str = Field(
        description='The version of the data contract.',
        examples=['v1'],
        title='Data contract version',
    )
    requests: list[Response] = Field(
        description='A response for each request that the provider has handled. JSON on the wire.',
        title='Responses',
    )
    encryption_secret: str | None = Field(
        None,
        alias='encryption-secret',
        description=(
            'The ID of a Juju secret with an `encryption-key` that the requirer uses to encrypt'
            ' sensitive fields, in a cross-model relation.'
        ),
        examples=['secret://bc7400b7-2fce-41dd-8509-14a984455cda/d7fmpmvmp25c7618tfc0'],
        title='Encryption secret ID',
    )
    data: str | None = Field(
        None,
        description=(
            'A JSON copy of the requests, by request ID, which the provider keeps to work out what'
            ' has changed.'
        ),
        examples=[
            '{"a0e66a95ec879066": {"resource": "app:*", "request-id": "a0e66a95ec879066",'
            ' "salt": "SALTSALTSALTSALT"}}'
        ],
        title='Request data copy',
    )

    @field_validator('requests', mode='before')
    @classmethod
    def _decode(cls, value: Any) -> Any:
        return _load_json(value)

    @field_serializer('requests')
    def _encode(self, value: list[Response]) -> str:
        return json.dumps([r.model_dump(by_alias=True) for r in value])


class RequirerAppData(_BareStringDatabag):
    """The requirer's application databag."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={'examples': [{'version': 'v1', 'requests': _REQUIRER_REQUESTS}]},
    )

    version: str = Field(
        description='The version of the data contract.',
        examples=['v1'],
        title='Data contract version',
    )
    requests: list[Request] = Field(
        description='The requests, one for each range of keys. JSON on the wire.',
        title='Requests',
    )
    encryption_secret: str | None = Field(
        None,
        alias='encryption-secret',
        description=(
            "A copy of the provider's `encryption-secret`, which the requirer writes in a"
            ' cross-model relation.'
        ),
        examples=['secret://bc7400b7-2fce-41dd-8509-14a984455cda/d7fmpmvmp25c7618tfc0'],
        title='Encryption secret ID',
    )

    @field_validator('requests', mode='before')
    @classmethod
    def _decode(cls, value: Any) -> Any:
        return _load_json(value)

    @field_serializer('requests')
    def _encode(self, value: list[Request]) -> str:
        return json.dumps([r.model_dump(by_alias=True) for r in value])


class RequirerUnitData(_BareStringDatabag):
    """The databag for each requirer unit."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            'examples': [
                {
                    'data': (
                        '{"a0e66a95ec879066": {"resource": "app:*", "request-id":'
                        ' "a0e66a95ec879066", "salt": "SALTSALTSALTSALT", "endpoints":'
                        ' "valkey-1.valkey-endpoints:6379", "mode": "sentinel"}}'
                    )
                }
            ]
        },
    )

    data: str | None = Field(
        None,
        description=(
            'A JSON copy of the last response for each request, by request ID, which the requirer'
            ' keeps to work out what has changed.'
        ),
        examples=['{"a0e66a95ec879066": {"resource": "app:*", "mode": "sentinel"}}'],
        title='Response data copy',
    )


ProviderUnitData = None
