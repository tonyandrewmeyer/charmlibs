# Copyright 2024 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the tracing interface."""

import enum

from pydantic import BaseModel, ConfigDict, Field, Json


class TransportProtocolType(str, enum.Enum):
    """Receiver Type."""

    http = "http"
    grpc = "grpc"


class ProtocolType(BaseModel):
    """Protocol Type."""

    model_config = ConfigDict(
        # Allow serializing enum values.
        use_enum_values=True
    )
    """Pydantic config."""

    name: str = Field(
        ...,
        description="Receiver protocol name. What protocols are supported (and what they are called) "
        "may differ per provider. For the protocols that the OpenTelemetry Collector supports, see "
        "https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver.",
        examples=["otlp_grpc", "otlp_http", "zipkin", "jaeger_thrift_http"],
    )
    type: TransportProtocolType = Field(
        ...,
        description="The transport protocol used by this receiver.",
        examples=["http", "grpc"],
    )


class Receiver(BaseModel):
    """Specification of an active receiver."""

    protocol: ProtocolType = Field(
        ...,
        description="Receiver protocol name and type.",
        examples=[{"name": "otlp_http", "type": "http"}, {"name": "otlp_grpc", "type": "grpc"}],
    )
    url: str = Field(
        ...,
        description="URL at which the receiver is reachable. If there's an ingress, this is the external URL. "
        "Otherwise, it's the service's FQDN or internal IP. "
        "If the protocol type is `grpc`, the URL has no scheme.",
        examples=[
            "http://traefik_address:2331",
            "https://traefik_address:2331",
            "http://tempo_public_ip:2331",
            "https://tempo_public_ip:2331",
            "tempo_public_ip:2331",
        ],
    )


class ProviderAppData(BaseModel):
    """Application databag schema for the provider side of the tracing interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "receivers": '[{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://traefik_address:2331"}, '
                    '{"protocol": {"name": "otlp_grpc", "type": "grpc"}, "url": "traefik_address:2331"}]',
                },
                {
                    "receivers": "[]",
                },
            ]
        }
    )

    receivers: Json[list[Receiver]] = Field(
        ...,
        description="The receivers that the provider has enabled, each with the protocol it uses and its resolvable URL. "
        "This is empty if the provider supports none of the requested protocols.",
        examples=[
            '[{"protocol": {"name": "otlp_grpc", "type": "grpc"}, "url": "tempo.cos.svc.cluster.local:4317"}]',
            "[]",
        ],
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
        description="The protocols that the requirer wants to use to send traces. "
        "The library accepts `zipkin`, `otlp_grpc`, `otlp_http`, `jaeger_grpc`, and `jaeger_thrift_http`.",
        examples=['["otlp_grpc", "otlp_http"]', '["otlp_http"]'],
    )


ProviderUnitData = None
RequirerUnitData = None
