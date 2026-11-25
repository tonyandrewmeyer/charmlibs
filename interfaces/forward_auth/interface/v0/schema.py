# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of `forward_auth`."""

from pydantic import BaseModel, ConfigDict, Field, Json


class ProviderAppData(BaseModel):
    """The provider's application databag."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'decisions_address': 'http://oauth2-proxy-k8s.mymodel.svc.cluster.local:4180',
                    'app_names': '["myapp", "otherapp"]',
                    'headers': '["X-Auth-Request-User", "X-Auth-Request-Email"]',
                },
                {
                    'decisions_address': 'http://oathkeeper.mymodel.svc.cluster.local:4456/decisions',
                    'app_names': '[]',
                    'headers': '[]',
                },
            ]
        }
    )

    decisions_address: str = Field(
        description=(
            'The address of the endpoint that decides whether a request is authenticated, '
            'which the requirer forwards requests to.'
        ),
        examples=[
            'http://oauth2-proxy-k8s.mymodel.svc.cluster.local:4180',
            'http://oathkeeper.mymodel.svc.cluster.local:4456/decisions',
            'grpc://authorization-service.mymodel.svc.cluster.local:9091',
        ],
    )
    app_names: Json[list[str]] = Field(
        description=(
            'The names of the applications that have asked to be protected '
            'by the Identity and Access Proxy, as a JSON list.'
        ),
        examples=['["myapp", "otherapp"]', '[]'],
    )
    headers: Json[list[str]] | None = Field(
        default=None,
        description=(
            "The headers to copy from the provider's response to the forwarded request, "
            'as a JSON list.'
        ),
        examples=['["X-Auth-Request-User", "X-Auth-Request-Email"]', '[]'],
    )


class RequirerAppData(BaseModel):
    """The requirer's application databag."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {'ingress_app_names': '["myapp", "otherapp"]'},
            ]
        }
    )

    ingress_app_names: Json[list[str]] | None = Field(
        default=None,
        description=(
            'The names of the applications that the requirer provides ingress to, as a JSON list.'
        ),
        examples=['["myapp", "otherapp"]', '[]'],
    )


ProviderUnitData = None
RequirerUnitData = None
