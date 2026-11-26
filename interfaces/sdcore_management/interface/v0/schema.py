"""This file defines the schemas for the provider and requirer sides of the `sdcore_management` relation interface."""

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"management_url": "http://1.2.3.4:1234"},
            ]
        }
    )

    management_url: HttpUrl = Field(
        description="The URL of the endpoint for managing the SD-Core network.",
        examples=["http://1.2.3.4:1234", "http://10.1.42.17:5000"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
