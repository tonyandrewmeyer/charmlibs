"""This file defines the schemas for the provider and requirer sides of the profiling interface."""

from pydantic import BaseModel, ConfigDict, Field, Json


class ProviderAppData(BaseModel):
    """Application databag schema for the provider side of the profiling interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'otlp_grpc_endpoint_url': '"pyroscope.cos.svc.cluster.local:42424"',
                    'insecure': 'true',
                },
                {
                    'otlp_grpc_endpoint_url': '"10.0.0.1:42424"',
                    'insecure': 'false',
                },
            ]
        }
    )

    otlp_grpc_endpoint_url: Json[str] = Field(
        description='The host and port at which the provider accepts profiles with OTLP over gRPC, without a scheme. '
        "This is the ingress address if the provider has one, and the provider's cluster-internal FQDN otherwise.",
        examples=['"pyroscope.cos.svc.cluster.local:42424"', '"10.0.0.1:42424"'],
    )
    insecure: bool = Field(
        default=False,
        description='Whether the ingestion endpoint must be accessed without TLS.',
        examples=['false', 'true'],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
