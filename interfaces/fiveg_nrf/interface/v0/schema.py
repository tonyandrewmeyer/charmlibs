"""This file defines the schemas for the provider and requirer sides of the `fiveg_nrf` interface."""

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"url": "https://sdcore-nrf-k8s:29510"},
            ]
        }
    )

    url: AnyHttpUrl = Field(
        description="The URL to reach the NRF.",
        examples=["https://sdcore-nrf-k8s:29510", "https://nrf-example.com:1234"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
