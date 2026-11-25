"""This file defines the schemas for the provider and requirer sides of the `tls-certificates` interface."""

import json

from pydantic import BaseModel, ConfigDict, Field, Json

CA_CERT = (
    "-----BEGIN CERTIFICATE-----\nMIIDWDCCAkCgAwIBAgIUJUSFtceIq3nb...\n-----END CERTIFICATE-----\n"
)
CERT = (
    "-----BEGIN CERTIFICATE-----\nMIIDizCCAnOgAwIBAgIUZ9a1J4X0kEw3...\n-----END CERTIFICATE-----\n"
)
CSR = "-----BEGIN CERTIFICATE REQUEST-----\nMIICvzCCAacCAQAwSzEaMBgGA1UEAwwR...\n-----END CERTIFICATE REQUEST-----\n"
CA_CSR = "-----BEGIN CERTIFICATE REQUEST-----\nMIICkDCCAXgCAQAwSzEaMBgGA1UEAwwM...\n-----END CERTIFICATE REQUEST-----\n"
IP_CSR = "-----BEGIN CERTIFICATE REQUEST-----\nMIICqTCCAZECAQAwQjERMA8GA1UEAwwI...\n-----END CERTIFICATE REQUEST-----\n"

CERTIFICATE_EXAMPLE = {
    "ca": CA_CERT,
    "certificate_signing_request": CSR,
    "certificate": CERT,
    "chain": [CERT, CA_CERT],
}
REQUEST_ERROR_EXAMPLE = {
    "csr": IP_CSR,
    "error": {
        "code": 101,
        "name": "ip_not_allowed",
        "message": "IP addresses are not allowed",
        "reason": "ip in san",
        "provider": "lego",
        "endpoint": "https://acme-staging-v02.api.letsencrypt.org/directory",
    },
}
CAPABILITIES_EXAMPLE = {
    "supports_ip_sans": False,
    "supports_wildcard_dns": True,
    "allowed_domains": ["example.com"],
    "provider_type": "acme",
}
CSRS_EXAMPLE = [
    {"certificate_signing_request": CSR, "ca": False},
    {"certificate_signing_request": CA_CSR, "ca": True},
]


class Certificate(BaseModel):
    """A certificate that the provider has issued for a certificate signing request."""

    ca: str = Field(
        description="The certificate of the CA that signed the certificate, in PEM format.",
        title="CA certificate",
        examples=[CA_CERT],
    )
    certificate_signing_request: str = Field(
        description="The certificate signing request that the certificate is for, in PEM format.",
        title="Certificate signing request",
        examples=[CSR],
    )
    certificate: str = Field(
        description="The certificate, in PEM format.",
        title="Certificate",
        examples=[CERT],
    )
    chain: list[str] | None = Field(
        default=None,
        description="The certificate chain, in PEM format, starting with the certificate itself.",
        title="Chain",
        examples=[[CERT, CA_CERT]],
    )
    recommended_expiry_notification_time: int | None = Field(
        default=None,
        description=(
            "How many hours before the certificate expires the requirer should be notified. "
            "Only older versions of the library write this."
        ),
        title="Recommended expiry notification time",
        examples=[168],
    )
    revoked: bool | None = Field(
        default=None,
        description="Whether the provider has revoked the certificate.",
        title="Revoked",
        examples=[True],
    )


class CertificateSigningRequest(BaseModel):
    """A certificate signing request from the requirer."""

    certificate_signing_request: str = Field(
        description="The certificate signing request, in PEM format.",
        title="Certificate signing request",
        examples=[CSR],
    )
    ca: bool | None = Field(
        default=None,
        description="Whether the certificate is for a certificate authority (CA).",
        title="CA",
        examples=[False, True],
    )


class ProviderError(BaseModel):
    """The reason that the provider couldn't issue a certificate."""

    code: int = Field(
        description=(
            "Numeric error code: 1XX for errors in the certificate signing request, "
            "2XX for server errors, and 9XX for other errors."
        ),
        title="Code",
        examples=[101, 102, 103, 201, 999],
    )
    name: str = Field(
        description="Machine-readable name of the error.",
        title="Name",
        examples=[
            "ip_not_allowed",
            "domain_not_allowed",
            "wildcard_not_allowed",
            "server_not_available",
        ],
    )
    message: str = Field(
        description="Error message set by the provider charm.",
        title="Message",
        examples=["IP addresses are not allowed"],
    )
    reason: str | None = Field(
        default=None,
        description="Further explanation of the error, such as an error message from the backend.",
        title="Reason",
        examples=["ip in san"],
    )
    provider: str | None = Field(
        default=None,
        description="The provider, such as the charm's name or its backend.",
        title="Provider",
        examples=["lego", "vault"],
    )
    endpoint: str | None = Field(
        default=None,
        description="The URL of the server that issues the certificates.",
        title="Endpoint",
        examples=["https://acme-staging-v02.api.letsencrypt.org/directory"],
    )


class RequestError(BaseModel):
    """A certificate signing request that the provider couldn't process."""

    csr: str = Field(
        description="The certificate signing request that failed, in PEM format.",
        title="Certificate signing request",
        examples=[IP_CSR],
    )
    error: ProviderError = Field(
        description="Details of the error.",
        title="Error",
        examples=[REQUEST_ERROR_EXAMPLE["error"]],
    )


class Capabilities(BaseModel):
    """Best-effort description of what the provider's certificate server supports.

    Every attribute is independently optional. An omitted attribute means "unspecified" and
    must not be treated as an assumed default.
    """

    supports_ip_sans: bool | None = Field(
        default=None,
        description="Whether IP addresses are accepted in SANs.",
        title="Supports IP SANs",
        examples=[False],
    )
    supports_wildcard_dns: bool | None = Field(
        default=None,
        description="Whether wildcard DNS entries are accepted.",
        title="Supports wildcard DNS",
        examples=[True],
    )
    supports_subdomain: bool | None = Field(
        default=None,
        description="Whether subdomain certificates can be issued.",
        title="Supports subdomain",
        examples=[False],
    )
    supports_ca_certificates: bool | None = Field(
        default=None,
        description="Whether CA certificates can be issued.",
        title="Supports CA certificates",
        examples=[True],
    )
    allowed_domains: list[str] | None = Field(
        default=None,
        description="The DNS domains that certificates can be issued for.",
        title="Allowed domains",
        examples=[["example.com"]],
    )
    provider_type: str | None = Field(
        default=None,
        description="The kind of provider.",
        title="Provider type",
        examples=["acme", "vault", "self-signed"],
    )


class ProviderAppData(BaseModel):
    """Provider application data model."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "certificates": json.dumps([CERTIFICATE_EXAMPLE]),
                },
                {
                    "certificates": json.dumps([CERTIFICATE_EXAMPLE]),
                    "request_errors": json.dumps([REQUEST_ERROR_EXAMPLE]),
                    "capabilities": json.dumps(CAPABILITIES_EXAMPLE),
                },
                {
                    "certificates": json.dumps([{**CERTIFICATE_EXAMPLE, "revoked": True}]),
                },
            ]
        }
    )

    certificates: Json[list[Certificate]] | None = Field(
        default=None,
        description="The certificates that the provider has issued, as a JSON list.",
        title="Certificates",
        examples=[json.dumps([CERTIFICATE_EXAMPLE])],
    )
    request_errors: Json[list[RequestError]] | None = Field(
        default=None,
        description=(
            "The certificate signing requests that the provider couldn't process, "
            "with the reason for each, as a JSON list."
        ),
        title="Request errors",
        examples=[json.dumps([REQUEST_ERROR_EXAMPLE])],
    )
    capabilities: Json[Capabilities] | None = Field(
        default=None,
        description="A best-effort description of what the provider's certificate server supports, as a JSON object.",
        title="Capabilities",
        examples=[json.dumps(CAPABILITIES_EXAMPLE)],
    )


class RequirerData(BaseModel):
    """Requirer data model.

    The same model is used for the unit and application data. Depending on its mode, a
    requirer writes its certificate signing requests to its unit databags, its application
    databag, or both, so either may be empty.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "certificate_signing_requests": json.dumps([
                        {"certificate_signing_request": CSR, "ca": False}
                    ]),
                },
                {
                    "certificate_signing_requests": json.dumps(CSRS_EXAMPLE),
                },
            ]
        }
    )

    certificate_signing_requests: Json[list[CertificateSigningRequest]] = Field(
        default_factory=list[CertificateSigningRequest],
        description="The certificate signing requests, as a JSON list.",
        title="Certificate signing requests",
        examples=[json.dumps(CSRS_EXAMPLE)],
    )


ProviderUnitData = None
RequirerAppData = RequirerData
RequirerUnitData = RequirerData
