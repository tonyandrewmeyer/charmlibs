# Copyright 2023 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the openfga interface."""

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class ProviderAppData(BaseModel):
    """Provider data schema for OpenFGA v0."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'store_id': '01GK13VYZK62Q1T0X55Q2BHYD6',
                    'token_secret_id': 'secret:cs8l6hvmp25c77r5ou5g',
                    'address': '10.10.0.17',
                    'scheme': 'http',
                    'port': '8080',
                    'dns_name': 'openfga-k8s-0.openfga-k8s-endpoints.mymodel.svc.cluster.local',
                },
                {
                    'store_id': '01GK13VYZK62Q1T0X55Q2BHYD6',
                    'token': 'test-token',
                    'address': '10.10.0.17',
                    'scheme': 'http',
                    'port': '8080',
                },
            ]
        }
    )

    address: IPvAnyAddress = Field(
        description='The address of the OpenFGA service.',
        title='OpenFGA address',
        examples=['10.10.0.17'],
    )
    port: int = Field(
        description='The port that the OpenFGA service listens on (HTTP).',
        title='OpenFGA port',
        examples=['8080'],
    )
    scheme: str = Field(
        description='The scheme to use to connect to the OpenFGA service.',
        title='OpenFGA scheme',
        examples=['http', 'https'],
    )
    dns_name: str | None = Field(
        default=None,
        description='The DNS name of the OpenFGA service.',
        title='OpenFGA DNS name',
        examples=['openfga-k8s-0.openfga-k8s-endpoints.mymodel.svc.cluster.local'],
    )
    token_secret_id: str | None = Field(
        default=None,
        description=(
            'The ID of the Juju secret that holds the preshared token to connect to the '
            'OpenFGA service, under the `token` key.'
        ),
        title='Secret ID of the OpenFGA token',
        examples=['secret:cs8l6hvmp25c77r5ou5g'],
    )
    token: str | None = Field(
        default=None,
        description=(
            'The preshared token to connect to the OpenFGA service, '
            'written when Juju secrets are not available.'
        ),
        title='The OpenFGA token',
        examples=['test-token'],
    )
    store_id: str | None = Field(
        default=None,
        description='The ID of the authorization store that was created.',
        title='OpenFGA store ID',
        examples=['01GK13VYZK62Q1T0X55Q2BHYD6'],
    )


class RequirerAppData(BaseModel):
    """Requirer data schema for OpenFGA v0."""

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
