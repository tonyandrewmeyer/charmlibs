# Copyright 2025 Canonical
# See LICENSE file for licensing details.
"""This file defines the schema for the provider side of the wazuh_api_client interface.

It defines one model, `ProviderAppData`.
"""

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'endpoint': 'https://wazuh.example.com:55000/',
                    'user_credentials_secret': 'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0',
                },
            ]
        }
    )

    endpoint: AnyHttpUrl = Field(
        description='The URL of the Wazuh server REST API.',
        title='Endpoint',
        examples=['https://wazuh.example.com:55000/', 'https://10.180.162.200:55000/'],
    )
    user_credentials_secret: str = Field(
        min_length=1,
        description='The ID of a Juju secret that holds the API credentials, under the `user` and `password` keys.',
        title='User credentials secret',
        examples=[
            'secret://59060ecc-0495-4a80-8006-5f1fc13fd783/cjqub6vubg2s77p3nio0',
            'secret:cjqub6vubg2s77p3nio0',
        ],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
