# Copyright 2023 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the ingress interface.

Every value in both databags is JSON-encoded.
"""

from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, Json


class Url(BaseModel):
    url: AnyHttpUrl = Field(
        description="The URL at which the requirer application is reachable through the ingress.",
        examples=["http://foo.bar/model_name-app_name"],
    )


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ingress": '{"url": "http://foo.bar/model_name-app_name"}',
                },
            ]
        }
    )

    ingress: Json[Url] = Field(
        description="A JSON object with a single `url` key, holding the URL at which the requirer application is reachable.",
        examples=['{"url": "http://foo.bar/model_name-app_name"}'],
    )


class HealthCheck(BaseModel):
    path: str = Field(description="The health check endpoint path.", examples=["/health"])
    scheme: str | None = Field(
        default=None,
        description="Replaces the server URL scheme for the health check endpoint.",
        examples=["http"],
    )
    hostname: str | None = Field(
        default=None,
        description="Hostname to be set in the health check request.",
        examples=["app.example.com"],
    )
    port: int | None = Field(
        default=None,
        description="Replaces the server URL port for the health check endpoint.",
        examples=[8081],
    )
    interval: str = Field(
        default="30s", description="Frequency of the health check calls.", examples=["30s"]
    )
    timeout: str = Field(
        default="5s", description="Maximum duration for a health check request.", examples=["5s"]
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "model": '"model_name"',
                    "name": '"app_name"',
                    "port": "4242",
                },
                {
                    "model": '"model_name"',
                    "name": '"app_name"',
                    "port": "443",
                    "is_port_open": "true",
                    "healthcheck_params": '{"path": "/health"}',
                    "strip-prefix": "true",
                    "redirect-https": "true",
                    "scheme": '"https"',
                },
            ]
        }
    )

    model: Json[str] = Field(
        description="The name of the model the requirer application is in.",
        examples=['"model_name"'],
    )
    name: Json[str] = Field(
        description="The name of the application requesting ingress.",
        examples=['"app_name"'],
    )
    port: Json[int] = Field(
        description="The port on the requirer's units that the ingress routes traffic to. The library only writes ports from 1 to 65534.",
        examples=["4242"],
    )
    is_port_open: Json[bool] = Field(
        default=False,
        description="Whether the requirer's leader unit has opened `port`. Omitted when false.",
        examples=["true"],
    )
    healthcheck_params: Json[HealthCheck] | None = Field(
        default=None,
        description="Health check configuration for the requirer's units, as a JSON object.",
        examples=['{"path": "/health"}', '{"path": "/ready", "interval": "10s", "timeout": "2s"}'],
    )
    strip_prefix: Json[bool | None] = Field(
        default=False,
        alias="strip-prefix",
        description="Whether the ingress should strip the URL's path prefix before forwarding a request to the requirer. Omitted when false.",
        examples=["true"],
    )
    redirect_https: Json[bool | None] = Field(
        default=False,
        alias="redirect-https",
        description="Whether the ingress should redirect HTTP requests to HTTPS. Omitted when false.",
        examples=["true"],
    )
    scheme: Json[Literal["http", "https", "h2c"]] = Field(
        default="http",
        description="The scheme that the ingress uses to reach the requirer's units. Omitted when `http`.",
        examples=['"https"', '"h2c"'],
    )


class RequirerUnitData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "host": '"app-0.app-endpoints.model_name.svc.cluster.local"',
                    "ip": '"10.1.2.3"',
                },
                {
                    "host": '"app-0.app-endpoints.model_name.svc.cluster.local"',
                },
            ]
        }
    )

    host: Json[str] = Field(
        description="The hostname at which the ingress can reach this unit. Defaults to the unit's FQDN.",
        examples=['"app-0.app-endpoints.model_name.svc.cluster.local"'],
    )
    ip: Json[str | None] = Field(
        default=None,
        description="The IP address (IPv4 or IPv6) at which the ingress can reach this unit. Defaults to the unit's bind address for the relation, and is omitted if Juju doesn't provide one.",
        examples=['"10.1.2.3"'],
    )


ProviderUnitData = None
