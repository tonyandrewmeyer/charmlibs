# Copyright 2024 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the tracing interface."""

from pydantic import BaseModel, ConfigDict, Field, Json


class Receiver(BaseModel):
    """Specification of an active receiver."""

    port: int = Field(
        ..., description="Port at which the receiver is listening.", examples=[4317, 4318]
    )
    protocol: str = Field(
        ...,
        description="Receiver protocol name. What protocols are supported (and what they are called) "
        "may differ per provider. The ones built into Tempo are `otlp_http` and `otlp_grpc`. For the "
        "protocols that the OpenTelemetry Collector supports, see "
        "https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver.",
        examples=["otlp_grpc", "otlp_http", "tempo_http", "jaeger_thrift_compact"],
    )


class ProviderAppData(BaseModel):
    """Application databag schema for the provider side of the tracing interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "host": '"tempo-k8s-0.tempo-k8s-endpoints.cos.svc.cluster.local"',
                    "receivers": '[{"protocol": "otlp_grpc", "port": 4317}, {"protocol": "otlp_http", "port": 4318}]',
                },
                {
                    "host": '"tempo-k8s-0.tempo-k8s-endpoints.cos.svc.cluster.local"',
                    "receivers": '[{"protocol": "otlp_http", "port": 4318}]',
                    "external_url": '"https://example.com/cos-tempo-k8s"',
                    "internal_scheme": '"https"',
                },
            ]
        }
    )

    host: Json[str] = Field(
        ...,
        description="Hostname of the tracing server.",
        examples=['"tempo-k8s-0.tempo-k8s-endpoints.cos.svc.cluster.local"'],
    )
    receivers: Json[list[Receiver]] = Field(
        ...,
        description="List of the receivers that this server has enabled, and their ports.",
        examples=[
            '[{"protocol": "otlp_grpc", "port": 4317}, {"protocol": "otlp_http", "port": 4318}]'
        ],
    )
    external_url: Json[str] | None = Field(
        default=None,
        description="The server's URL. If there's an ingress, this is the ingress address.",
        examples=['"https://example.com/cos-tempo-k8s"'],
    )
    internal_scheme: Json[str] | None = Field(
        default=None,
        description="The scheme that the server accepts for communication inside the cluster.",
        examples=['"http"', '"https"'],
    )


class RequirerAppData(BaseModel):
    """Application databag schema for the requirer side of the tracing interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "receivers": '["otlp_grpc", "otlp_http"]',
                },
            ]
        }
    )

    receivers: Json[list[str]] = Field(
        ...,
        description="List of protocols that the requirer wishes to use.",
        examples=['["otlp_grpc", "otlp_http"]'],
    )


ProviderUnitData = None
RequirerUnitData = None
