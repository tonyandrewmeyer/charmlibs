"""This file defines the schemas for the provider and requirer sides of the `fiveg_core_gnb` relation interface."""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, Json


@dataclass
class PLMNConfig:
    """Dataclass representing the configuration for a PLMN."""

    mcc: str = Field(
        description="The Mobile Country Code.",
        examples=["001", "208", "302"],
        pattern=r"^[0-9][0-9][0-9]$",
    )
    mnc: str = Field(
        description="The Mobile Network Code.",
        examples=["01", "001", "999"],
        pattern=r"^[0-9][0-9][0-9]?$",
    )
    sst: int = Field(
        description="The Slice/Service Type of the network slice.",
        examples=[1, 2, 3, 4],
        ge=0,
        le=255,
    )
    sd: int | None = Field(
        description="The Slice Differentiator of the network slice. `null` if the slice has none.",
        default=None,
        examples=[1],
        ge=0,
        le=16777215,
    )


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "tac": "1",
                    "plmns": '[{"mcc": "001", "mnc": "01", "sst": 1, "sd": 1}]',
                },
                {
                    "tac": "2",
                    "plmns": '[{"mcc": "001", "mnc": "01", "sst": 1, "sd": null}, {"mcc": "208", "mnc": "93", "sst": 2, "sd": 102030}]',
                },
            ]
        }
    )

    tac: int = Field(
        description="The Tracking Area Code that the gNodeB is configured with.",
        examples=["1"],
        ge=1,
        le=16777215,
    )
    plmns: Json[list[PLMNConfig]] = Field(
        description="The PLMNs (Public Land Mobile Networks) that the gNodeB serves, as a JSON list.",
        examples=['[{"mcc": "001", "mnc": "01", "sst": 1, "sd": 1}]'],
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"gnb-name": "gnb001"},
            ]
        }
    )

    gnb_name: str = Field(
        alias="gnb-name",
        description="The unique name of the CU or gNodeB.",
        examples=["gnb001", "mymodel-oai-ran-cu-cu"],
    )


ProviderUnitData = None
RequirerUnitData = None
