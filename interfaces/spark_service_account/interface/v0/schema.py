"""This file defines the schemas for the provider and requirer sides of this relation interface."""

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


_REQUESTED_SECRETS = (
    '["username", "password", "tls", "tls-ca", "uris", "read-only-uris",'
    ' "entity-name", "entity-password", "spark-properties", "resource-manifest"]'
)


class ProviderAppData(_BareStringDatabag):
    """The provider's application databag."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "service-account": "test-namespace:test-service-account",
                    "secret-extra": (
                        "secret://59c8c4df-deca-4d79-83e1-18ff563042d1/d0q6mcvmp25c7650r87g"
                    ),
                    "data": json.dumps({
                        "requested-secrets": _REQUESTED_SECRETS,
                        "provided-secrets": '["mtls-cert"]',
                        "service-account": "test-namespace:test-service-account",
                        "skip-creation": "false",
                    }),
                },
                {
                    "service-account": "spark:kyuubi",
                    "spark-properties": (
                        '{"spark.kubernetes.namespace": "spark",'
                        ' "spark.kubernetes.authenticate.driver.serviceAccountName": "kyuubi"}'
                    ),
                    "resource-manifest": (
                        "apiVersion: v1\nkind: ServiceAccount\nmetadata:\n"
                        "  name: kyuubi\n  namespace: spark\n"
                    ),
                },
            ]
        },
    )

    service_account: str = Field(
        alias="service-account",
        description=(
            "The service account that the provider has set up, as `<namespace>:<name>`. This"
            " is the `service-account` that the requirer asked for."
        ),
        examples=["test-namespace:test-service-account"],
        title="Service account",
    )

    secret_extra: str | None = Field(
        default=None,
        alias="secret-extra",
        description=(
            "The ID of the Juju secret that has the service account's configuration. The"
            " secret's `spark-properties` key has the Spark properties for the service"
            " account, as a JSON object, and its `resource-manifest` key has the YAML"
            " manifest of the service account's Kubernetes resources. Not set if Juju"
            " secrets aren't supported, in which case `spark-properties` and"
            " `resource-manifest` are in the databag instead."
        ),
        examples=["secret://59c8c4df-deca-4d79-83e1-18ff563042d1/d0q6mcvmp25c7650r87g"],
        title="Service account configuration secret ID",
    )

    spark_properties: str | None = Field(
        default=None,
        alias="spark-properties",
        description=(
            "The Spark properties for the service account, as a JSON object. Only written"
            " here if Juju secrets aren't supported; otherwise it's in the `secret-extra`"
            " secret."
        ),
        examples=['{"spark.kubernetes.namespace": "spark"}'],
        title="Spark properties",
    )

    resource_manifest: str | None = Field(
        default=None,
        alias="resource-manifest",
        description=(
            "The YAML manifest of the service account's Kubernetes resources. Only written"
            " here if Juju secrets aren't supported; otherwise it's in the `secret-extra`"
            " secret."
        ),
        examples=["apiVersion: v1\nkind: ServiceAccount\nmetadata:\n  name: kyuubi\n"],
        title="Resource manifest",
    )

    data: dict[str, Any] | None = Field(
        default=None,
        description=(
            "The requirer's application databag as the provider last saw it, used by the"
            " library to work out what changed. A JSON object on the wire."
        ),
        examples=[{"service-account": "spark:kyuubi", "skip-creation": "false"}],
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
                    "service-account": "test-namespace:test-service-account",
                    "requested-secrets": _REQUESTED_SECRETS,
                    "provided-secrets": '["mtls-cert"]',
                    "skip-creation": "false",
                },
                {
                    "service-account": "spark:kyuubi",
                    "skip-creation": "true",
                },
            ]
        },
    )

    service_account: str = Field(
        alias="service-account",
        description=("The service account that the requirer wants, as `<namespace>:<name>`."),
        examples=["test-namespace:test-service-account"],
        title="Service account",
    )

    requested_secrets: list[str] | None = Field(
        default=None,
        alias="requested-secrets",
        description=(
            "The provider fields that the requirer wants in Juju secrets rather than in the"
            " databag. A JSON array on the wire. The library always includes"
            " `spark-properties` and `resource-manifest`, as well as the data_interfaces"
            " defaults, which this interface doesn't use. Not set if Juju secrets aren't"
            " supported."
        ),
        examples=[["spark-properties", "resource-manifest"]],
        title="Requested secrets",
    )

    provided_secrets: list[str] | None = Field(
        default=None,
        alias="provided-secrets",
        description=(
            "The requirer fields that the requirer puts in Juju secrets rather than in the"
            " databag. A JSON array on the wire. The library writes the data_interfaces"
            " default, which this interface doesn't use."
        ),
        examples=[["mtls-cert"]],
        title="Provided secrets",
    )

    skip_creation: str | None = Field(
        default=None,
        alias="skip-creation",
        description=(
            "`true` if the provider should use an existing service account rather than"
            " create one, or `false`. The provider treats anything other than `true`"
            " (ignoring case), including leaving it out, as `false`."
        ),
        examples=["false", "true"],
        title="Skip creation",
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
                    "requested-secrets": _REQUESTED_SECRETS,
                    "provided-secrets": '["mtls-cert"]',
                    "data": json.dumps({
                        "service-account": "test-namespace:test-service-account",
                        "secret-extra": (
                            "secret://59c8c4df-deca-4d79-83e1-18ff563042d1/d0q6mcvmp25c7650r87g"
                        ),
                    }),
                },
            ]
        },
    )

    requested_secrets: list[str] | None = Field(
        default=None,
        alias="requested-secrets",
        description=(
            "A copy of `requested-secrets` from the application databag. A JSON array on the wire."
        ),
        examples=[["spark-properties", "resource-manifest"]],
        title="Requested secrets",
    )

    provided_secrets: list[str] | None = Field(
        default=None,
        alias="provided-secrets",
        description=(
            "A copy of `provided-secrets` from the application databag. A JSON array on the wire."
        ),
        examples=[["mtls-cert"]],
        title="Provided secrets",
    )

    data: dict[str, Any] | None = Field(
        default=None,
        description=(
            "The provider's application databag as the requirer last saw it, used by the"
            " library to work out what changed. A JSON object on the wire."
        ),
        examples=[
            {
                "service-account": "spark:kyuubi",
                "secret-extra": "secret://59c8c4df-deca-4d79-83e1-18ff563042d1/d0q6mcvmp25c7650r87g",
            }
        ],
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
