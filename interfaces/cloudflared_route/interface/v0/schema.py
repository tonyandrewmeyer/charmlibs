# Copyright 2024 Canonical
# See LICENSE file for licensing details.
"""This file defines the schema for the provider side of the cloudflared-route interface.

It defines one model, `ProviderAppData`.
"""

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class ProviderAppData(BaseModel):
    """Provider application databag schema for the cloudflared-route interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "tunnel_token_secret_id": "secret:csn5caau557j9bojn7rg",
                    "nameserver": "1.1.1.1",
                },
            ]
        }
    )

    tunnel_token_secret_id: str = Field(
        description=(
            "The ID of a Juju secret that has the cloudflared tunnel token under the "
            "`tunnel-token` key."
        ),
        title="Tunnel token secret ID",
        examples=["secret:csn5caau557j9bojn7rg"],
    )
    nameserver: IPvAnyAddress | None = Field(
        default=None,
        description=(
            "The IPv4 or IPv6 address of the DNS nameserver that the cloudflared tunnel uses. "
            "If it's not set, the tunnel uses the system's default nameserver."
        ),
        title="Nameserver",
        examples=["1.1.1.1", "10.152.183.10", "2606:4700:4700::1111"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
