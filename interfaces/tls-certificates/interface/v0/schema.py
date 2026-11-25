# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Schemas for the provider and requirer sides of the `tls-certificates` interface (v0)."""

import json

from pydantic import BaseModel, ConfigDict, Field, Json, model_validator

CA_CERT = (
    "-----BEGIN CERTIFICATE-----\nMIIDazCCAlOgAwIBAgIUcmcehy58Qe+g...\n-----END CERTIFICATE-----\n"
)
CERT = (
    "-----BEGIN CERTIFICATE-----\nMIIDajCCAlKgAwIBAgIUaKRAIcZmkNzi...\n-----END CERTIFICATE-----\n"
)
KEY = (
    "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA1CHw0NwHmuu/...\n"
    "-----END RSA PRIVATE KEY-----\n"
)


class CertificateRequest(BaseModel):
    """A request for a certificate."""

    common_name: str = Field(
        description="The common name to include in the certificate.",
        title="Common name",
        examples=["myapp.example.com"],
    )
    sans: list[str] | None = Field(
        default=None,
        description="The subject alternative names to include in the certificate.",
        title="SANs",
        examples=[["myapp.example.com", "10.0.0.1"]],
    )


class CertificateAndKey(BaseModel):
    """A certificate and its private key."""

    cert: str = Field(
        description="The certificate, in PEM format.",
        title="Certificate",
        examples=[CERT],
    )
    key: str = Field(
        description="The private key for the certificate, in PEM format.",
        title="Private key",
        examples=[KEY],
    )


class ProviderUnitData(BaseModel):
    """Provider unit data model.

    As well as `ca`, `chain`, and `unit_name`, the databag has a key for the common name of
    each certificate that the provider has issued. Its value is a JSON object with the
    certificate (`cert`) and its private key (`key`).
    """

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "examples": [
                {
                    "ca": CA_CERT,
                    "chain": CA_CERT,
                    "myapp.example.com": json.dumps({"key": KEY, "cert": CERT}),
                },
            ]
        },
    )
    __pydantic_extra__: dict[str, Json[CertificateAndKey]]

    ca: str = Field(
        description="The CA certificate, in PEM format.",
        title="CA certificate",
        examples=[CA_CERT],
    )
    chain: str = Field(
        description="The CA chain, in PEM format.",
        title="Chain",
        examples=[CA_CERT],
    )
    unit_name: str | None = Field(
        default=None,
        description="The name of the unit.",
        title="Unit name",
        examples=["vault-0"],
    )


class RequirerUnitData(BaseModel):
    """Requirer unit data model.

    The requirer writes `cert_requests`, `client_cert_requests`, or both.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "cert_requests": json.dumps([
                        {
                            "common_name": "myapp.example.com",
                            "sans": ["myapp.example.com", "10.0.0.1"],
                        }
                    ]),
                },
                {
                    "unit_name": "myapp-0",
                    "cert_requests": json.dumps([
                        {"common_name": "myapp.example.com", "sans": []}
                    ]),
                    "client_cert_requests": json.dumps([
                        {"common_name": "myapp-client", "sans": []}
                    ]),
                },
            ]
        }
    )

    unit_name: str | None = Field(
        default=None,
        description="The name of the unit.",
        title="Unit name",
        examples=["myapp-0"],
    )
    cert_requests: Json[list[CertificateRequest]] | None = Field(
        default=None,
        description="The requests for server certificates, as a JSON list.",
        title="Server certificate requests",
        examples=[
            json.dumps([{"common_name": "myapp.example.com", "sans": ["myapp.example.com"]}])
        ],
    )
    client_cert_requests: Json[list[CertificateRequest]] | None = Field(
        default=None,
        description="The requests for client certificates, as a JSON list.",
        title="Client certificate requests",
        examples=[json.dumps([{"common_name": "myapp-client", "sans": []}])],
    )

    @model_validator(mode="after")
    def _has_requests(self):
        if self.cert_requests is None and self.client_cert_requests is None:
            raise ValueError("at least one of cert_requests and client_cert_requests is required")
        return self


ProviderAppData = None
RequirerAppData = None
