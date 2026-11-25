# Copyright 2023 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the ingress interface.

Requirer values are plain strings; the provider's `ingress` value is a YAML mapping.
"""

import yaml
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


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
                    "ingress": "url: http://foo.bar/model_name-app_name\n",
                },
            ]
        }
    )

    ingress: Url = Field(
        description="A YAML mapping with a single `url` key, holding the URL at which the requirer application is reachable.",
        examples=["url: http://foo.bar/model_name-app_name\n"],
    )

    @field_validator("ingress", mode="before")
    @classmethod
    def decode_ingress(cls, value: object) -> object:
        return yaml.safe_load(value) if isinstance(value, str) else value


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "model": "model_name",
                    "name": "app_name",
                    "host": "app-0.app-endpoints.model_name.svc.cluster.local",
                    "port": "4242",
                },
                {
                    "model": "model_name",
                    "name": "app_name",
                    "host": "app-0.app-endpoints.model_name.svc.cluster.local",
                    "port": "4242",
                    "strip-prefix": "true",
                    "redirect-https": "true",
                },
            ]
        }
    )

    model: str = Field(
        description="The name of the model the requirer application is in.",
        examples=["model_name"],
    )
    name: str = Field(
        description="The name of the application requesting ingress.",
        examples=["app_name"],
    )
    host: str = Field(
        description="The hostname at which the ingress can reach the requirer's leader unit. Defaults to the leader's FQDN.",
        examples=["app-0.app-endpoints.model_name.svc.cluster.local"],
    )
    port: str = Field(
        description="The port on the requirer's leader unit that the ingress routes traffic to, as a decimal integer.",
        examples=["4242"],
    )
    strip_prefix: str | None = Field(
        default=None,
        alias="strip-prefix",
        description="`true` if the ingress should strip the URL's path prefix before forwarding a request to the requirer. Any other value, or no value, means false.",
        examples=["true"],
    )
    redirect_https: str | None = Field(
        default=None,
        alias="redirect-https",
        description="`true` if the ingress should redirect HTTP requests to HTTPS. Any other value, or no value, means false.",
        examples=["true"],
    )


ProviderUnitData = None
RequirerUnitData = None
