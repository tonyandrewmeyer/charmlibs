"""This file defines the schemas for the provider and requirer sides of the `certificate_transfer` interface (v0)."""

import json

from pydantic import BaseModel, ConfigDict, Field, Json, model_validator

CA_CERT = (
    '-----BEGIN CERTIFICATE-----\nMIIDUDCCAjigAwIBAgIUJZ3V9DkTYg...\n-----END CERTIFICATE-----\n'
)
INTERMEDIATE_CERT = (
    '-----BEGIN CERTIFICATE-----\nMIIDUDCCAjigAwIBAgIUKeSsO9fJUv...\n-----END CERTIFICATE-----\n'
)


class ProviderUnitData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'certificate': INTERMEDIATE_CERT,
                    'ca': CA_CERT,
                    'chain': json.dumps([INTERMEDIATE_CERT, CA_CERT]),
                    'version': '0',
                },
                {
                    'certificate': json.dumps(CA_CERT),
                    'ca': json.dumps(CA_CERT),
                    'chain': json.dumps([CA_CERT]),
                    'version': '0',
                },
            ]
        }
    )

    certificate: str | None = Field(
        default=None,
        description=(
            'A public TLS certificate, in PEM format. '
            'Version 1 of the library writes this as a JSON-encoded string.'
        ),
        title='Certificate',
        examples=[INTERMEDIATE_CERT],
    )
    ca: str | None = Field(
        default=None,
        description=(
            'The public certificate of the CA, in PEM format. '
            'Version 1 of the library writes this as a JSON-encoded string.'
        ),
        title='CA certificate',
        examples=[CA_CERT],
    )
    chain: Json[list[str]] | None = Field(
        default=None,
        description='The CA chain, as a JSON list of certificates in PEM format.',
        title='CA chain',
        examples=[json.dumps([INTERMEDIATE_CERT, CA_CERT])],
    )
    version: int | None = Field(
        default=None,
        description='The version of the interface used in this databag.',
        title='Interface version',
        examples=['0'],
    )

    @model_validator(mode='after')
    def _has_a_certificate(self):
        if self.certificate is None and self.ca is None and self.chain is None:
            raise ValueError('at least one of certificate, ca, and chain is required')
        return self


class RequirerAppData(BaseModel):
    model_config = ConfigDict(json_schema_extra={'examples': [{'version': '0'}]})

    version: int | None = Field(
        default=None,
        description=(
            'The version of the interface that the requirer supports. '
            'A requirer that sets this to `1` gets the v1 data instead.'
        ),
        title='Interface version',
        examples=['0'],
    )


ProviderAppData = None
RequirerUnitData = None
