"""This file defines the schemas for the provider and requirer sides of the `fiveg_gnb_identity` relation interface."""

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"gnb_name": "gnb001", "tac": "1"},
            ]
        }
    )

    gnb_name: str = Field(
        description="The name of the gNodeB.",
        examples=["gnb001"],
    )
    tac: int = Field(
        description="The Tracking Area Code that the gNodeB is configured with.",
        examples=["1"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
