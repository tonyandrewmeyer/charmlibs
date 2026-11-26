# Copyright 2023 Canonical
# See LICENSE file for licensing details.
"""This file defines the schema for the provider side of the saml interface.

It defines one model, `ProviderAppData`.
"""

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "entity_id": "https://login.ubuntu.com",
                    "metadata_url": "https://login.ubuntu.com/saml/metadata",
                    "x509certs": "MIIC6DCCAdCgAwIBAgIUW42TU9LSjEZLMCclWrvSwAsgRtcwDQYJKoZIhvcNAQEL",
                    "single_sign_on_service_redirect_url": "https://login.ubuntu.com/saml/",
                    "single_sign_on_service_redirect_binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                    "single_sign_on_service_post_url": "https://login.ubuntu.com/saml/",
                    "single_sign_on_service_post_binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                    "single_logout_service_redirect_url": "https://login.ubuntu.com/+logout",
                    "single_logout_service_redirect_binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                {
                    "entity_id": "urn:example:idp",
                    "x509certs": "MIIC6DCCAdCgAwIBAgIUW42TU9LSjEZLMCclWrvSwAsgRtcwDQYJKoZIhvcNAQEL,MIIDBzCCAe+gAwIBAgIJAPr/Mrlc8EGhMA0GCSqGSIb3DQEBBQUAMBoxGDAWBgNV",
                    "single_sign_on_service_redirect_url": "https://idp.example.com/sso",
                    "single_sign_on_service_redirect_binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                    "single_logout_service_redirect_url": "https://idp.example.com/slo",
                    "single_logout_service_redirect_binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                    "single_logout_service_redirect_response_url": "https://idp.example.com/slo/response",
                    "single_logout_service_post_url": "https://idp.example.com/slo",
                    "single_logout_service_post_binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                    "single_logout_service_post_response_url": "https://idp.example.com/slo/post-response",
                },
            ]
        }
    )

    entity_id: str = Field(
        min_length=1,
        description="Identifier of the IdP entity. This is a URI, but not necessarily a URL.",
        title="Entity ID",
        examples=["https://login.ubuntu.com", "urn:example:idp"],
    )
    metadata_url: AnyHttpUrl | None = Field(
        default=None,
        description="URL to the IdP's metadata. Not set when the provider was given the metadata directly.",
        title="Metadata URL",
        examples=["https://login.ubuntu.com/saml/metadata"],
    )
    x509certs: str = Field(
        description=(
            "Comma-separated list of the IdP's public X.509 certificates, as they appear in the "
            "`X509Certificate` elements of the metadata: base64-encoded DER, without PEM headers."
        ),
        title="Public IdP certificates",
        examples=[
            "MIIC6DCCAdCgAwIBAgIUW42TU9LSjEZLMCclWrvSwAsgRtcwDQYJKoZIhvcNAQEL",
            "MIIC6DCCAdCgAwIBAgIUW42TU9LSjEZLMCclWrvSwAsgRtcwDQYJKoZIhvcNAQEL,MIIDBzCCAe+gAwIBAgIJAPr/Mrlc8EGhMA0GCSqGSIb3DQEBBQUAMBoxGDAWBgNV",
        ],
    )
    single_sign_on_service_redirect_url: AnyHttpUrl = Field(
        description="URL of the IdP's `SingleSignOnService` endpoint with the HTTP-Redirect binding, where the SP sends authentication requests.",
        title="SSO REDIRECT URL",
        examples=["https://login.ubuntu.com/saml/"],
    )
    single_sign_on_service_redirect_binding: str = Field(
        description="SAML protocol binding of the HTTP-Redirect `SingleSignOnService` endpoint.",
        title="SSO REDIRECT binding",
        examples=["urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"],
    )
    single_sign_on_service_post_url: AnyHttpUrl | None = Field(
        default=None,
        description="URL of the IdP's `SingleSignOnService` endpoint with the HTTP-POST binding, if it has one.",
        title="SSO POST URL",
        examples=["https://login.ubuntu.com/saml/"],
    )
    single_sign_on_service_post_binding: str | None = Field(
        default=None,
        description="SAML protocol binding of the HTTP-POST `SingleSignOnService` endpoint.",
        title="SSO POST binding",
        examples=["urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"],
    )
    single_logout_service_redirect_url: AnyHttpUrl | None = Field(
        default=None,
        description="URL of the IdP's `SingleLogoutService` endpoint with the HTTP-Redirect binding, if it has one.",
        title="SLO REDIRECT URL",
        examples=["https://login.ubuntu.com/+logout"],
    )
    single_logout_service_redirect_binding: str | None = Field(
        default=None,
        description="SAML protocol binding of the HTTP-Redirect `SingleLogoutService` endpoint.",
        title="SLO REDIRECT binding",
        examples=["urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"],
    )
    single_logout_service_redirect_response_url: AnyHttpUrl | None = Field(
        default=None,
        description="URL where the IdP expects the REDIRECT `<LogoutResponse>`, if it differs from `single_logout_service_redirect_url`.",
        title="SLO REDIRECT response URL",
        examples=["https://idp.example.com/slo/response"],
    )
    single_logout_service_post_url: AnyHttpUrl | None = Field(
        default=None,
        description="URL of the IdP's `SingleLogoutService` endpoint with the HTTP-POST binding, if it has one.",
        title="SLO POST URL",
        examples=["https://idp.example.com/slo"],
    )
    single_logout_service_post_binding: str | None = Field(
        default=None,
        description="SAML protocol binding of the HTTP-POST `SingleLogoutService` endpoint.",
        title="SLO POST binding",
        examples=["urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"],
    )
    single_logout_service_post_response_url: AnyHttpUrl | None = Field(
        default=None,
        description="URL where the IdP expects the POST `<LogoutResponse>`, if it differs from `single_logout_service_post_url`.",
        title="SLO POST response URL",
        examples=["https://idp.example.com/slo/post-response"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
