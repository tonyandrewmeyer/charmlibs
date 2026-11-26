# Copyright 2026 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the ingress_per_unit interface.

It defines two models, `ProviderAppData` and `RequirerUnitData`.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'ingress': (
                        'prometheus-k8s/0:\n'
                        '  url: http://foo.bar/cos-prometheus-k8s-0\n'
                        'prometheus-k8s/1:\n'
                        '  url: http://foo.bar/cos-prometheus-k8s-1\n'
                    ),
                },
            ]
        }
    )

    ingress: str = Field(
        description=(
            'A YAML-encoded mapping from the name of each requirer unit that has ingress to an '
            'object with a `url` key. In `http` mode, the url is the full URL at which ingress is '
            'provided for that unit. In `tcp` mode, it is the `host:port` at which the unit can be '
            'reached, without a scheme.'
        ),
        title='Ingress',
        examples=[
            'prometheus-k8s/0:\n  url: http://foo.bar/cos-prometheus-k8s-0\n',
            'kafka-k8s/0:\n  url: foo.bar:9092\n',
        ],
    )


class RequirerUnitData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'model': 'cos',
                    'name': 'prometheus-k8s/0',
                    'host': 'prometheus-k8s-0.prometheus-k8s-endpoints.cos.svc.cluster.local',
                    'port': '9090',
                    'mode': 'http',
                    'scheme': 'https',
                    'strip-prefix': 'true',
                    'redirect-https': 'true',
                },
            ]
        }
    )

    model: str = Field(
        description='The name of the model the unit requesting ingress is in. All units of the requirer must give the same model.',
        title='Model name',
        examples=['cos'],
    )
    name: str = Field(
        description='The name of the unit requesting ingress. The provider uses it as the key for the unit in `ingress`.',
        title='Unit name',
        examples=['prometheus-k8s/0'],
    )
    host: str = Field(
        description='The hostname or address at which the provider can reach the unit.',
        title='Host',
        examples=['prometheus-k8s-0.prometheus-k8s-endpoints.cos.svc.cluster.local'],
    )
    port: int = Field(
        description='The port on the unit to expose.',
        title='Port',
        examples=['9090'],
    )
    mode: Literal['http', 'tcp'] = Field(
        default='http',
        description='Whether the unit is to be exposed over HTTP or as plain TCP.',
        title='Mode',
        examples=['http', 'tcp'],
    )
    scheme: Literal['http', 'https'] = Field(
        default='http',
        description='The scheme the unit itself serves on, which the provider uses to reach it.',
        title='Scheme',
        examples=['http', 'https'],
    )
    strip_prefix: bool = Field(
        default=False,
        alias='strip-prefix',
        description=(
            'Whether the provider should strip the path prefix from requests before forwarding '
            'them to the unit. The ingress URL still includes the prefix. Written as `true` only '
            'when set; the provider treats any other value as false.'
        ),
        title='Strip prefix',
        examples=['true'],
    )
    redirect_https: bool = Field(
        default=False,
        alias='redirect-https',
        description=(
            'Whether the provider should redirect HTTP requests to HTTPS. Written as `true` only '
            'when set; the provider treats any other value as false.'
        ),
        title='Redirect HTTPS',
        examples=['true'],
    )


ProviderUnitData = None
RequirerAppData = None
