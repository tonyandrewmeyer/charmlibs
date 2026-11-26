"""This file defines the schemas for the provider and requirer sides of the `login_ui_endpoints` interface."""

from pydantic import BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "consent_url": "https://example.com/mymodel-login-ui/ui/consent",
                    "error_url": "https://example.com/mymodel-login-ui/ui/error",
                    "login_url": "https://example.com/mymodel-login-ui/ui/login",
                    "oidc_error_url": "https://example.com/mymodel-login-ui/ui/oidc_error",
                    "device_verification_url": "https://example.com/mymodel-login-ui/ui/device_code",
                    "post_device_done_url": "https://example.com/mymodel-login-ui/ui/device_complete",
                    "recovery_url": "https://example.com/mymodel-login-ui/ui/reset_email",
                    "registration_url": "https://example.com/mymodel-login-ui/ui/register",
                    "settings_url": "https://example.com/mymodel-login-ui/ui/manage_details",
                    "webauthn_settings_url": "https://example.com/mymodel-login-ui/ui/setup_passkey",
                    "account_linking_settings_url": "https://example.com/mymodel-login-ui/ui/manage_connected_accounts",
                    "verification_url": "https://example.com/mymodel-login-ui/ui/verification",
                },
                {
                    "consent_url": "/ui/consent",
                    "error_url": "/ui/error",
                    "login_url": "/ui/login",
                    "oidc_error_url": "/ui/oidc_error",
                    "device_verification_url": "/ui/device_code",
                    "post_device_done_url": "/ui/device_complete",
                    "recovery_url": "/ui/reset_email",
                    "registration_url": "/ui/register",
                    "settings_url": "/ui/manage_details",
                    "webauthn_settings_url": "/ui/setup_passkey",
                    "account_linking_settings_url": "/ui/manage_connected_accounts",
                    "verification_url": "/ui/verification",
                },
                {
                    "consent_url": "https://example.com/mymodel-login-ui/ui/consent",
                    "login_url": "https://example.com/mymodel-login-ui/ui/login",
                    "byosso_enabled": "true",
                },
            ]
        }
    )

    consent_url: str | None = Field(
        default=None,
        description="The page that Hydra sends users to, to give consent to an OAuth client.",
        examples=["https://example.com/mymodel-login-ui/ui/consent", "/ui/consent"],
    )
    error_url: str | None = Field(
        default=None,
        description="The page that Kratos sends users to, to show an error.",
        examples=["https://example.com/mymodel-login-ui/ui/error", "/ui/error"],
    )
    login_url: str | None = Field(
        default=None,
        description="The page that Hydra and Kratos send users to, to log in.",
        examples=["https://example.com/mymodel-login-ui/ui/login", "/ui/login"],
    )
    oidc_error_url: str | None = Field(
        default=None,
        description="The page that Hydra sends users to, to show an OAuth 2.0 or OpenID Connect error.",
        examples=["https://example.com/mymodel-login-ui/ui/oidc_error", "/ui/oidc_error"],
    )
    device_verification_url: str | None = Field(
        default=None,
        description="The page that Hydra sends users to, to enter the code for the device authorization flow.",
        examples=["https://example.com/mymodel-login-ui/ui/device_code", "/ui/device_code"],
    )
    post_device_done_url: str | None = Field(
        default=None,
        description="The page that Hydra sends users to when the device authorization flow is complete.",
        examples=[
            "https://example.com/mymodel-login-ui/ui/device_complete",
            "/ui/device_complete",
        ],
    )
    recovery_url: str | None = Field(
        default=None,
        description="The page that Kratos sends users to, to recover their account.",
        examples=["https://example.com/mymodel-login-ui/ui/reset_email", "/ui/reset_email"],
    )
    registration_url: str | None = Field(
        default=None,
        description="The page that Kratos sends users to, to register.",
        examples=["https://example.com/mymodel-login-ui/ui/register", "/ui/register"],
    )
    settings_url: str | None = Field(
        default=None,
        description="The page that Kratos sends users to, to change their settings. Kratos also uses it as the default page to return to.",
        examples=["https://example.com/mymodel-login-ui/ui/manage_details", "/ui/manage_details"],
    )
    webauthn_settings_url: str | None = Field(
        default=None,
        description="The page that Kratos sends users to, to set up a WebAuthn key.",
        examples=["https://example.com/mymodel-login-ui/ui/setup_passkey", "/ui/setup_passkey"],
    )
    account_linking_settings_url: str | None = Field(
        default=None,
        description="The page that Kratos sends users to, to manage the accounts linked from external identity providers.",
        examples=[
            "https://example.com/mymodel-login-ui/ui/manage_connected_accounts",
            "/ui/manage_connected_accounts",
        ],
    )
    verification_url: str | None = Field(
        default=None,
        description="The page that Kratos sends users to, to verify their account.",
        examples=["https://example.com/mymodel-login-ui/ui/verification", "/ui/verification"],
    )
    byosso_enabled: str | None = Field(
        default=None,
        description="Whether the login UI runs in Bring Your Own SSO mode, in which it decides when multi-factor authentication is needed. Written as `true` when it does.",
        examples=["true"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
