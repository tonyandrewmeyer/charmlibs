"""This file defines the schemas for the provider and requirer sides of the `ip_router` interface."""

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, IPvAnyNetwork, Json


class Route(BaseModel):
    destination: IPvAnyNetwork = Field(
        description="The network that the route leads to.",
        examples=["172.250.0.0/16"],
    )
    gateway: IPvAnyAddress = Field(
        description="The address of the next hop, which is in the network that has the route.",
        examples=["192.168.250.3"],
    )


class IPNetwork(BaseModel):
    network: IPvAnyNetwork = Field(
        description="The network, in CIDR notation.",
        examples=["192.168.250.0/24"],
    )
    gateway: IPvAnyAddress = Field(
        description="The address of the router's interface in the network.",
        examples=["192.168.250.1"],
    )
    routes: list[Route] | None = Field(
        default=None,
        description="The routes from this network to other networks.",
        examples=[[{"destination": "172.250.0.0/16", "gateway": "192.168.250.3"}]],
    )


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "networks": '{"access": {"network": "192.168.250.0/24", "gateway": "192.168.250.1", "routes": [{"destination": "172.250.0.0/16", "gateway": "192.168.250.3"}]}, "core": {"network": "192.168.251.0/24", "gateway": "192.168.251.1"}}',
                },
            ]
        }
    )

    networks: Json[dict[str, IPNetwork]] = Field(
        description="The routing table: every network that any requirer has requested, keyed by network name, as a JSON object.",
        examples=[
            '{"access": {"network": "192.168.250.0/24", "gateway": "192.168.250.1"}, "core": {"network": "192.168.251.0/24", "gateway": "192.168.251.1"}}'
        ],
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "networks": '{"access": {"network": "192.168.250.0/24", "gateway": "192.168.250.1", "routes": [{"destination": "172.250.0.0/16", "gateway": "192.168.250.3"}]}}',
                },
            ]
        }
    )

    networks: Json[dict[str, IPNetwork]] = Field(
        description="The networks that the requirer requests, keyed by network name, as a JSON object.",
        examples=['{"access": {"network": "192.168.250.0/24", "gateway": "192.168.250.1"}}'],
    )


ProviderUnitData = None
RequirerUnitData = None
