"""This file defines the schemas for the provider and requirer sides of the `sdcore_config` relation interface."""

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"webui_url": "sdcore-nms-k8s:9876"},
            ]
        }
    )

    webui_url: str = Field(
        description="The gRPC address of the configuration service, as `<host>:<port>`.",
        examples=["sdcore-nms-k8s:9876", "sdcore-webui-k8s:9876"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
