"""This file defines the schemas for the provider and requirer sides of the `hydra_endpoints` interface."""

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "admin_endpoint": "http://hydra.mymodel.svc.cluster.local:4445",
                    "public_endpoint": "http://hydra.mymodel.svc.cluster.local:4444",
                },
                {
                    "admin_endpoint": "https://hydra.example.com",
                    "public_endpoint": "https://hydra.example.com",
                },
            ]
        }
    )

    admin_endpoint: str = Field(
        description="The URL of Hydra's admin API.",
        examples=["http://hydra.mymodel.svc.cluster.local:4445", "https://hydra.example.com"],
    )
    public_endpoint: str = Field(
        description="The URL of Hydra's public API.",
        examples=["http://hydra.mymodel.svc.cluster.local:4444", "https://hydra.example.com"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
