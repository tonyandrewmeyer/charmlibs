"""This file defines the schemas for the provider and requirer sides of the `fiveg_f1` interface."""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, Json, conlist


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
                    "f1_ip_address": "192.168.70.132",
                    "f1_port": "2153",
                    "tac": "1",
                    "plmns": '[{"mcc": "001", "mnc": "01", "sst": 1, "sd": 1}]',
                },
            ]
        }
    )

    f1_ip_address: IPvAnyAddress = Field(
        description="The IPv4 address of the CU's network interface for F1 traffic.",
        examples=["192.168.70.132"],
    )
    f1_port: int = Field(
        description="The port that the CU uses for F1 traffic.",
        examples=["2153"],
    )
    tac: int = Field(
        description="The Tracking Area Code that the CU is configured with.",
        examples=["1"],
        ge=1,
        le=16777215,
    )
    plmns: Json[conlist(PLMNConfig, min_length=1)] = Field(
        description="The PLMNs (Public Land Mobile Networks) that the CU serves, as a JSON list.",
        examples=['[{"mcc": "001", "mnc": "01", "sst": 1, "sd": 1}]'],
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"f1_port": "2152"},
            ]
        }
    )

    f1_port: int = Field(
        description="The port that the DU uses for F1 traffic.",
        examples=["2152"],
    )


ProviderUnitData = None
RequirerUnitData = None
