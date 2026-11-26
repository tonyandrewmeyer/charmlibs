"""This file defines the schemas for the provider and requirer sides of the filesystem_info interface.

It defines one model, `ProviderAppData`.
"""

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    """App databag model for the `filesystem_info` interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "endpoint": "lustre://(192.168.227.11%40tcp1%2C192.168.227.12%40tcp1)/?fs-name=lustre",
                },
            ]
        }
    )

    endpoint: str = Field(
        description="A URI with the information needed to mount the exported filesystem. The scheme is the filesystem type, and the hosts are in parentheses.",
        title="Endpoint",
        examples=[
            "nfs://(192.168.1.1)/export",
            "nfs://(nfs.example.com%3A2049)/srv/data?version=4",
            "cephfs://fsuser@(10.0.0.1%3A6789%2C10.0.0.2%3A6789%2C10.0.0.3%3A6789)/?fsid=354ca7c4-f10d-11ee-93f8-1f85f87b7845&name=scratch&auth=secret%3Ad0erdhvmp25c7e3pa0ug&auth-rev=1",
            "lustre://(192.168.227.11%40tcp1%2C192.168.227.12%40tcp1)/?fs-name=lustre",
        ],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
