"""Schemas for v0 of the s3 interface."""

import json
from enum import IntEnum
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_serializer, field_validator


class S3APIVersion(IntEnum):
    v2 = 2
    v4 = 4


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
    """Data expected on the provider side for the s3 v0 interface."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "bucket": "minio",
                    "access-key": "RANDOM",
                    "secret-key": "RANDOM",
                    "path": "relation-68",
                    "endpoint": "https://minio-endpoint/",
                    "region": "us-east-1",
                    "s3-uri-style": "path",
                    "storage-class": "glacier",
                    "tls-ca-chain": '["-----BEGIN CERTIFICATE-----\\nMIIB...\\n-----END CERTIFICATE-----"]',
                    "s3-api-version": "4",
                    "attributes": '["Cache-Control=max-age=90000", "X-Amz-Server-Side-Encryption-Customer-Key=CuStoMerKey="]',
                    "data": '{"bucket": "relation-68"}',
                },
                {
                    "version": "1",
                    "access-key": "RANDOM",
                    "secret-key": "RANDOM",
                    "endpoint": "https://minio-endpoint/",
                    "attributes": "Cache-Control=max-age=90000,X-Amz-Server-Side-Encryption-Customer-Key=CuStoMerKey=",
                },
            ]
        },
    )

    bucket: str | None = Field(
        default=None,
        description=(
            "The bucket/container name delivered by the provider. Providers using the v1"
            " library only write it when it's configured on the provider."
        ),
        examples=["minio"],
        title="Bucket name",
    )

    access_key: str | None = Field(
        default=None,
        alias="access-key",
        description="Access key ID (account) for connecting to the object storage.",
        examples=["username"],
        title="Access key ID",
    )

    secret_key: SecretStr | None = Field(
        default=None,
        alias="secret-key",
        description="Secret access key (password) for connecting to the object storage.",
        examples=["alphanum-32byte-random"],
        title="Secret access key",
    )

    path: str | None = Field(
        default=None,
        description="The path inside the bucket/container to store objects.",
        examples=["relation-24"],
        title="Path",
    )

    endpoint: str | None = Field(
        default=None,
        description="The endpoint used to connect to the object storage.",
        examples=["https://minio-endpoint/"],
        title="Endpoint URL",
    )

    region: str | None = Field(
        default=None,
        description="The region used to connect to the object storage.",
        examples=["us-east-1"],
        title="Region",
    )

    s3_uri_style: str | None = Field(
        default=None,
        alias="s3-uri-style",
        description="The S3 protocol specific bucket path lookup type: path or host.",
        examples=["path", "host"],
        title="S3 URI style",
    )

    storage_class: str | None = Field(
        default=None,
        alias="storage-class",
        description="Storage class for objects uploaded to the object storage.",
        examples=["glacier"],
        title="Storage class",
    )

    tls_ca_chain: list[str] | None = Field(
        default=None,
        alias="tls-ca-chain",
        description=(
            "The complete CA chain, which can be used for HTTPS validation, as a list of"
            " PEM certificates. A JSON array on the wire."
        ),
        examples=[["-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----"]],
        title="TLS CA chain",
    )

    s3_api_version: S3APIVersion | None = Field(
        default=None,
        alias="s3-api-version",
        description="S3 protocol specific API signature. A decimal string on the wire.",
        examples=[2, 4],
        strict=False,
        title="S3 API signature",
    )

    attributes: list[str] | str | None = Field(
        default=None,
        description=(
            "The custom metadata (HTTP headers). Providers using the v0 library write a JSON"
            " array of strings; providers using the v1 library write their configured string"
            " unchanged."
        ),
        examples=[
            [
                "Cache-Control=max-age=90000,min-fresh=9000",
                "X-Amz-Server-Side-Encryption-Customer-Key=CuStoMerKey=",
            ],
        ],
        title="Custom metadata",
    )

    delete_older_than_days: int | None = Field(
        default=None,
        alias="delete-older-than-days",
        description="Delete objects older than this many days. A decimal string on the wire.",
        examples=[30],
        strict=False,
        title="Delete objects older than (days)",
    )

    version: str | None = Field(
        default=None,
        description=(
            "The schema version, written by providers using the v1 library. Providers using the"
            " v0 library don't write it."
        ),
        examples=["1"],
        title="Schema version",
    )

    data: dict[str, str] | None = Field(
        default=None,
        description=(
            "The requirer's application databag as last seen by the provider, used by the v0"
            " library to compute diffs. A JSON object on the wire."
        ),
        examples=[{"bucket": "relation-68"}],
        title="Last seen requirer data",
    )

    @field_serializer("secret_key")
    def _reveal(self, value: SecretStr | None) -> str | None:
        """Write the real secret to the databag rather than the masked repr."""
        return None if value is None else value.get_secret_value()

    @field_serializer("s3_api_version")
    def _dump_api_version(self, value: S3APIVersion | None) -> str | None:
        """Write the signature as a decimal string; Ops will error on a non-string."""
        return None if value is None else str(value.value)

    @field_serializer("delete_older_than_days")
    def _dump_int(self, value: int | None) -> str | None:
        return None if value is None else str(value)

    @field_validator("tls_ca_chain", "data", mode="before")
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value  # __init__ argument was already deserialized.
        return json.loads(value)

    @field_serializer("tls_ca_chain", "data")
    def _dump_json(self, value: object) -> str | None:
        if value is None:
            return None
        return json.dumps(value)

    @field_validator("attributes", mode="before")
    @classmethod
    def _load_json_array_or_string(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value  # __init__ argument was already deserialized.
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return value
        if isinstance(loaded, list):
            return cast("list[Any]", loaded)  # Elements are validated by Pydantic.
        return value

    @field_serializer("attributes")
    def _dump_json_array_or_string(self, value: list[str] | str | None) -> str | None:
        if isinstance(value, list):
            return json.dumps(value)
        return value


class RequirerAppData(_BareStringDatabag):
    """Data expected on the requirer side for the s3 v0 interface."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={"examples": [{"bucket": "myapp"}, {"bucket": "relation-17"}]},
    )

    bucket: str = Field(
        description=(
            "The bucket name requested by the requirer, or relation-<id> if it has no name"
            " to request."
        ),
        examples=["myapp", "relation-17"],
        title="Bucket name",
    )


ProviderUnitData = None
RequirerUnitData = None
