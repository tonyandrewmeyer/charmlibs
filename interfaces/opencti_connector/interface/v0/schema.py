# Copyright 2025 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the opencti_connector interface.

It defines two models, `ProviderAppData` and `RequirerAppData`.
"""

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'connector_charm_name': 'opencti-crowdstrike-connector',
                    'connector_type': 'EXTERNAL_IMPORT',
                    'connector_id': '4aeba4a3-3b80-438e-97e1-1c06a188b690',
                },
                {
                    'connector_charm_name': 'wazuh-server',
                    'connector_type': 'EXTERNAL_IMPORT',
                },
            ]
        }
    )

    connector_charm_name: str = Field(
        description='The name of the connector charm. OpenCTI uses it to name the user that it creates for the connector.',
        title='Connector charm name',
        examples=['opencti-crowdstrike-connector', 'wazuh-server'],
    )
    connector_type: str = Field(
        description='The OpenCTI connector type. OpenCTI uses it to choose the privileges of the user that it creates for the connector. See the [OpenCTI documentation](https://docs.opencti.io/latest/deployment/connectors/#connector-configuration).',
        title='Connector type',
        examples=[
            'EXTERNAL_IMPORT',
            'INTERNAL_ENRICHMENT',
            'INTERNAL_IMPORT_FILE',
            'INTERNAL_EXPORT_FILE',
            'STREAM',
        ],
    )
    connector_id: str | None = Field(
        default=None,
        description='A UUID that the connector generates once and uses as its OpenCTI connector ID. OpenCTI does not read it.',
        title='Connector ID',
        examples=['4aeba4a3-3b80-438e-97e1-1c06a188b690'],
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'opencti_url': 'http://opencti-endpoints.stg-opencti.svc:8080',
                    'opencti_token': 'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0',
                },
            ]
        }
    )

    opencti_url: AnyHttpUrl = Field(
        description='The URL that OpenCTI is reachable at, without a trailing slash.',
        title='OpenCTI URL',
        examples=['http://opencti-endpoints.stg-opencti.svc:8080', 'https://opencti.example.com'],
    )
    opencti_token: str = Field(
        description='The ID of a Juju secret that holds the API token of the OpenCTI user for this connector, under the `token` key.',
        title='OpenCTI token',
        examples=['secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0'],
    )


ProviderUnitData = None
RequirerUnitData = None
