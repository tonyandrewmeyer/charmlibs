"""This file defines the schemas for the provider and requirer sides of the `certificate_transfer` interface (v1)."""

import json

from pydantic import BaseModel, ConfigDict, Field, Json

CA_CERT = (
    '-----BEGIN CERTIFICATE-----\nMIIDUDCCAjigAwIBAgIUJZ3V9DkTYg...\n-----END CERTIFICATE-----\n'
)
OTHER_CA_CERT = (
    '-----BEGIN CERTIFICATE-----\nMIIDUDCCAjigAwIBAgIUKeSsO9fJUv...\n-----END CERTIFICATE-----\n'
)


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'certificates': json.dumps([CA_CERT, OTHER_CA_CERT]),
                    'version': '1',
                },
                {
                    'certificates': '[]',
                    'version': '1',
                },
            ]
        }
    )

    certificates: Json[set[str]] = Field(
        description=(
            'The certificates to transfer to the requirer, as a JSON list of '
            'certificates in PEM format. The list is empty when there are none.'
        ),
        title='Certificates',
        examples=[json.dumps([CA_CERT, OTHER_CA_CERT]), '[]'],
    )
    version: int = Field(
        default=1,
        description='The version of the interface used in this databag.',
        title='Interface version',
        examples=['1'],
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(json_schema_extra={'examples': [{'version': '1'}]})

    version: int = Field(
        default=1,
        description=(
            'The version of the interface that the requirer supports. '
            'Without `1` here, the provider uses v0.'
        ),
        title='Interface version',
        examples=['1'],
    )


ProviderUnitData = None
RequirerUnitData = None
