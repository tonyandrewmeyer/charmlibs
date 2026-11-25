"""This file defines the schemas for the provider and requirer sides of the `fiveg_n2` interface."""

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "amf_ip_address": "192.168.70.132",
                    "amf_hostname": "amf",
                    "amf_port": "38412",
                },
            ]
        }
    )

    amf_ip_address: IPvAnyAddress = Field(
        description="The IP address to reach the AMF's N2 interface.",
        examples=["192.168.70.132"],
    )
    amf_hostname: str = Field(
        description="The hostname to reach the AMF's N2 interface.",
        examples=["amf", "sdcore-amf-k8s-external.mymodel.svc.cluster.local"],
    )
    amf_port: int = Field(
        description="The port to reach the AMF's N2 interface.",
        examples=["38412"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
