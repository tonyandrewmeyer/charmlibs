# Copyright 2025 Canonical
# See LICENSE file for licensing details.

from pydantic import BaseModel, ConfigDict, Field


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


_REQUESTED_SECRETS_EXAMPLE = (
    '["username", "password", "tls", "tls-ca", "uris", "read-only-uris", "entity-name",'
    ' "entity-password"]'
)


class ProviderAppData(_BareStringDatabag):
    """The provider's application databag."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            'examples': [
                {
                    'endpoints': '10.73.32.13:2379,10.73.32.136:2379,10.73.32.238:2379',
                    'secret-tls': 'secret://9d39bbbe-d95a-405d-8573-6835864daf92/cuvbv6p34trs48a10a2g',
                    'secret-user': 'secret://9d39bbbe-d95a-405d-8573-6835864daf92/cuvbv6p34trs48a10a30',
                    'version': '3.6.5',
                },
                {
                    'endpoints': '10.73.32.13:2379,10.73.32.136:2379,10.73.32.238:2379',
                    'secret-tls': 'secret://9d39bbbe-d95a-405d-8573-6835864daf92/cuvbv6p34trs48a10a2g',
                    'secret-user': 'secret://9d39bbbe-d95a-405d-8573-6835864daf92/cuvbv6p34trs48a10a30',
                    'version': '3.6.5',
                    'prefix': '/test/',
                    'resource': '/test/',
                    'salt': 'AHepBD0UYtY57DPo',
                },
            ]
        },
    )

    endpoints: str = Field(
        description='A comma-separated list of the etcd client endpoints.',
        title='etcd endpoints',
        examples=['10.73.32.13:2379,10.73.32.136:2379'],
    )

    version: str = Field(
        description='The version of etcd.',
        title='etcd version',
        examples=['3.6.5'],
    )

    secret_tls: str = Field(
        alias='secret-tls',
        description=(
            "The ID of a Juju secret with the CA certificate of the server under the `tls-ca` key"
            ' (and, from older providers, `True` under the `tls` key).'
        ),
        title='TLS secret ID',
        examples=['secret://9d39bbbe-d95a-405d-8573-6835864daf92/cuvbv6p34trs48a10a2g'],
    )

    secret_user: str = Field(
        alias='secret-user',
        description=(
            'The ID of a Juju secret with the etcd user information: the name of the user created'
            ' for the requirer under the `username` key, and a comma-separated list of the'
            " cluster's client URLs under the `uris` key."
        ),
        title='User secret ID',
        examples=['secret://9d39bbbe-d95a-405d-8573-6835864daf92/cuvbv6p34trs48a10a30'],
    )

    prefix: str | None = Field(
        None,
        description="A copy of the requirer's `prefix`, which the provider writes back.",
        title='Key prefix',
        examples=['/test/'],
    )

    resource: str | None = Field(
        None,
        description="A copy of the requirer's `prefix`, under the name the library uses for it.",
        title='Resource',
        examples=['/test/'],
    )

    salt: str | None = Field(
        None,
        description='A random string that the library generates for the request.',
        title='Salt',
        examples=['AHepBD0UYtY57DPo'],
    )

    encryption_secret: str | None = Field(
        None,
        alias='encryption-secret',
        description=(
            'The ID of a Juju secret with an `encryption-key` that the requirer uses to encrypt'
            ' `mtls-cert`, in a cross-model relation.'
        ),
        title='Encryption secret ID',
        examples=['secret://9d39bbbe-d95a-405d-8573-6835864daf92/cuvbv6p34trs48a10a3g'],
    )

    data: str | None = Field(
        None,
        description=(
            "A JSON copy of the requirer's request, which the provider keeps to work out what has"
            ' changed.'
        ),
        title='Request data copy',
        examples=['{"resource": "/test/", "salt": "AHepBD0UYtY57DPo"}'],
    )


class RequirerAppData(_BareStringDatabag):
    """The requirer's application databag."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            'examples': [
                {
                    'prefix': '/test/',
                    'secret-mtls': 'secret://9d39bbbe-d95a-405d-8573-6835864daf92/1a2b3c4d5e6f7g8h9i0j',
                    'requested-secrets': _REQUESTED_SECRETS_EXAMPLE,
                    'provided-secrets': '["mtls-cert"]',
                },
            ]
        },
    )

    prefix: str = Field(
        description='The prefix of the range of keys that the requirer wants to access.',
        title='Key prefix',
        examples=['/my/keys/'],
    )

    secret_mtls: str | None = Field(
        None,
        alias='secret-mtls',
        description=(
            'The ID of a Juju secret with the client certificate, in PEM format, under the'
            ' `mtls-cert` key.'
        ),
        title='mTLS secret ID',
        examples=['secret://9d39bbbe-d95a-405d-8573-6835864daf92/1a2b3c4d5e6f7g8h9i0j'],
    )

    mtls_cert: str | None = Field(
        None,
        alias='mtls-cert',
        description=(
            'The client certificate, encrypted with the key in the provider\'s'
            ' `encryption-secret`, in a cross-model relation, where it can\'t be in a secret.'
        ),
        title='mTLS certificate',
        examples=['gAAAAABpZ3J5cHRlZC1jZXJ0aWZpY2F0ZQ=='],
    )

    requested_secrets: str = Field(
        alias='requested-secrets',
        description=(
            'The provider fields that should be sent in Juju secrets. A JSON array on the wire.'
        ),
        title='Requested secrets',
        examples=[_REQUESTED_SECRETS_EXAMPLE],
    )

    provided_secrets: str = Field(
        alias='provided-secrets',
        description=(
            'The requirer fields that the requirer sends in Juju secrets. A JSON array on the'
            ' wire.'
        ),
        title='Provided secrets',
        examples=['["mtls-cert"]'],
    )

    encryption_secret: str | None = Field(
        None,
        alias='encryption-secret',
        description=(
            "A copy of the provider's `encryption-secret`, which the requirer writes in a"
            ' cross-model relation.'
        ),
        title='Encryption secret ID',
        examples=['secret://9d39bbbe-d95a-405d-8573-6835864daf92/cuvbv6p34trs48a10a3g'],
    )


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

    requested_secrets: str | None = Field(
        None,
        alias='requested-secrets',
        description='A copy of `requested-secrets` from the application databag.',
        title='Requested secrets',
        examples=[_REQUESTED_SECRETS_EXAMPLE],
    )

    provided_secrets: str | None = Field(
        None,
        alias='provided-secrets',
        description='A copy of `provided-secrets` from the application databag.',
        title='Provided secrets',
        examples=['["mtls-cert"]'],
    )


ProviderUnitData = None
