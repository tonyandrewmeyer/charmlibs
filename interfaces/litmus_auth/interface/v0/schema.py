"""This file defines the schemas for the provider and requirer sides of the litmus_auth interface.

Both sides write the same fields to their application databag.
"""

from pydantic import BaseModel, ConfigDict, Field, Json


class AppSchema(BaseModel):
    """Application databag schema for the provider and requirer sides of the litmus_auth interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'grpc_server_host': '"litmus-auth-k8s.chaos.svc.cluster.local"',
                    'grpc_server_port': '3030',
                    'insecure': 'true',
                    'version': '0',
                },
                {
                    'grpc_server_host': '"litmus-backend-k8s.chaos.svc.cluster.local"',
                    'grpc_server_port': '8001',
                    'insecure': 'false',
                    'version': '0',
                },
            ]
        }
    )

    grpc_server_host: Json[str] = Field(
        description='The hostname or IP address of the Litmus auth or backend gRPC server.',
        examples=['"litmus-auth-k8s.chaos.svc.cluster.local"', '"10.64.140.43"'],
    )
    grpc_server_port: int = Field(
        description='The port of the Litmus auth or backend gRPC server.',
        examples=['3030', '8001'],
    )
    insecure: bool = Field(
        default=False,
        description='Whether the gRPC server must be accessed without TLS.',
        examples=['false', 'true'],
    )
    version: int = Field(
        default=0,
        description='The version of this data model.',
        examples=['0'],
    )


ProviderAppData = AppSchema
ProviderUnitData = None
RequirerAppData = AppSchema
RequirerUnitData = None
