"""This file defines the schemas for the provider and requirer sides of the `fiveg_n3` interface."""

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"upf_ip_address": "192.168.252.3"},
            ]
        }
    )

    upf_ip_address: str = Field(
        description="The IP address of the UPF's N3 (access) interface.",
        examples=["192.168.252.3"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
