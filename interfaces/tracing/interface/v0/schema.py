# Copyright 2023 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the tracing interface."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, Json


class IngesterProtocol(str, Enum):
    jaeger_grpc = "jaeger_grpc"
    jaeger_http_thrift = "jaeger_http_thrift"
    otlp_grpc = "otlp_grpc"
    otlp_http = "otlp_http"
    zipkin = "zipkin"
    tempo = "tempo"


class Ingester(BaseModel):
    port: int = Field(
        ..., description="Port at which the ingester is listening.", examples=[4317, 4318]
    )
    protocol: IngesterProtocol = Field(
        ...,
        description="The tracing protocol that the ingester accepts.",
        examples=["otlp_grpc", "otlp_http"],
    )


class ProviderAppData(BaseModel):
    """Application databag schema for the provider side of the tracing interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "host": '"tempo-k8s-0.tempo-k8s-endpoints.cos.svc.cluster.local"',
                    "ingesters": '[{"protocol": "otlp_grpc", "port": 1234}, {"protocol": "otlp_http", "port": 5678}]',
                },
            ]
        }
    )

    host: Json[str] = Field(
        ...,
        description="Hostname at which the tracing server is reachable.",
        examples=['"tempo-k8s-0.tempo-k8s-endpoints.cos.svc.cluster.local"'],
    )
    ingesters: Json[list[Ingester]] = Field(
        ...,
        description="The ports and protocols that the tracing server accepts traces on.",
        examples=[
            '[{"protocol": "otlp_grpc", "port": 1234}, {"protocol": "otlp_http", "port": 5678}]'
        ],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
