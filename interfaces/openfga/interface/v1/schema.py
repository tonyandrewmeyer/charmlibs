# Copyright 2023 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the openfga interface."""

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    """Provider data schema for OpenFGA v1."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'grpc_api_url': 'openfga-k8s.mymodel.svc.cluster.local:8081',
                    'http_api_url': 'http://openfga-k8s.mymodel.svc.cluster.local:8080',
                    'store_id': '01GK13VYZK62Q1T0X55Q2BHYD6',
                    'token_secret_id': 'secret:cs8l6hvmp25c77r5ou5g',
                },
                {
                    'grpc_api_url': 'openfga-k8s.mymodel.svc.cluster.local:8081',
                    'http_api_url': 'http://openfga-k8s.mymodel.svc.cluster.local:8080',
                },
                {
                    'grpc_api_url': 'http://10.10.0.17:8081',
                    'http_api_url': 'http://10.10.0.17:8080',
                    'store_id': '01GK13VYZK62Q1T0X55Q2BHYD6',
                    'token': 'test-token',
                },
            ]
        }
    )

    grpc_api_url: str = Field(
        description='The URL of the gRPC API.',
        title='gRPC URL',
        examples=['openfga-k8s.mymodel.svc.cluster.local:8081', 'http://10.10.0.17:8081'],
    )
    http_api_url: str = Field(
        description='The URL of the HTTP API.',
        title='HTTP URL',
        examples=['http://openfga-k8s.mymodel.svc.cluster.local:8080', 'http://10.10.0.17:8080'],
    )
    token_secret_id: str | None = Field(
        description=(
            'The ID of the Juju secret that holds the preshared token to connect to the '
            'OpenFGA service, under the `token` key.'
        ),
        title='Secret ID of the OpenFGA token',
        examples=['secret:cs8l6hvmp25c77r5ou5g'],
        default=None,
    )
    token: str | None = Field(
        description=(
            'The preshared token to connect to the OpenFGA service. Older providers '
            'wrote this when Juju secrets were not available.'
        ),
        title='The OpenFGA token',
        examples=['test-token'],
        default=None,
    )
    store_id: str | None = Field(
        description='The ID of the authorization store that was created.',
        title='OpenFGA store ID',
        examples=['01GK13VYZK62Q1T0X55Q2BHYD6'],
        default=None,
    )


class RequirerAppData(BaseModel):
    """Requirer data schema for OpenFGA v1."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {'store_name': 'test-store'},
            ]
        }
    )

    store_name: str = Field(
        description='The name of the authorization store.',
        title='Authorization store name',
        examples=['test-store', 'auth_store'],
    )


ProviderUnitData = None
RequirerUnitData = None
