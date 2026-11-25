"""This file defines the schemas for the provider and requirer sides of the `fiveg_rfsim` interface."""

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "version": "0",
                    "rfsim_address": "192.168.70.130",
                    "sst": "1",
                    "sd": "1",
                    "band": "77",
                    "dl_freq": "4059090000",
                    "carrier_bandwidth": "106",
                    "numerology": "1",
                    "start_subcarrier": "541",
                },
            ]
        }
    )

    version: int | None = Field(
        default=None,
        description="The version of the `fiveg_rfsim` interface that the provider uses.",
        examples=["0"],
        ge=0,
    )
    rfsim_address: str = Field(
        description="The address of the RF simulator service, which is the DU's pod IP address.",
        examples=["192.168.70.130"],
    )
    sst: int = Field(
        description="The Slice/Service Type of the network slice.",
        examples=["1", "2", "3", "4"],
        ge=0,
        le=255,
    )
    sd: int | None = Field(
        description="The Slice Differentiator of the network slice. Not set if the slice has none.",
        default=None,
        examples=["1"],
        ge=0,
        le=16777215,
    )
    band: int | None = Field(
        default=None,
        description="The frequency band.",
        examples=["34", "77", "102"],
        gt=0,
    )
    dl_freq: int | None = Field(
        default=None,
        description="The downlink frequency, in Hz.",
        examples=["4059090000"],
        ge=410000000,
    )
    carrier_bandwidth: int | None = Field(
        default=None,
        description="The carrier bandwidth, as the number of downlink PRBs (Physical Resource Blocks).",
        examples=["106"],
        ge=11,
        le=273,
    )
    numerology: int | None = Field(
        default=None,
        description="The numerology, which sets the subcarrier spacing.",
        examples=["0", "1", "2", "3"],
        ge=0,
        le=6,
    )
    start_subcarrier: int | None = Field(
        default=None,
        description="The first usable subcarrier.",
        examples=["530", "541"],
        ge=0,
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"version": "0"},
            ]
        }
    )

    version: int | None = Field(
        default=None,
        description="The version of the `fiveg_rfsim` interface that the requirer uses.",
        examples=["0"],
        ge=0,
    )


ProviderUnitData = None
RequirerUnitData = None
