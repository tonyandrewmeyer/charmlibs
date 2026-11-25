"""This file defines the schemas for the provider and requirer sides of the `fiveg_n4` interface."""

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "upf_hostname": "upf.uplane-cloud.canonical.com",
                    "upf_port": "8805",
                },
            ]
        }
    )

    upf_hostname: str = Field(
        description="The name of the host that exposes the UPF's N4 interface.",
        examples=[
            "upf.uplane-cloud.canonical.com",
            "sdcore-upf-k8s-external.mymodel.svc.cluster.local",
        ],
    )
    upf_port: int = Field(
        description="The port on which the UPF's N4 interface is exposed.",
        examples=["8805"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
