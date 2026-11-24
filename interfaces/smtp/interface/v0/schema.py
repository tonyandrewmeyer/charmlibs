# Copyright 2023 Canonical
# See LICENSE file for licensing details.
"""This file defines the schema for the provider side of the smtp interface.

It defines one model, `ProviderAppData`.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, Json


class TransportSecurity(str, Enum):
    """Represent the transport security values."""

    NONE = "none"
    STARTTLS = "starttls"
    TLS = "tls"


class AuthType(str, Enum):
    """Represent the auth type values."""

    NONE = "none"
    NOT_PROVIDED = "not_provided"
    PLAIN = "plain"


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "host": "example.com",
                    "port": "587",
                    "user": "example_user",
                    "password_id": "secret:123213123123123123123",
                    "auth_type": "plain",
                    "transport_security": "tls",
                    "domain": "example.com",
                    "skip_ssl_verify": "False",
                },
            ]
        }
    )

    host: str = Field(
        min_length=1,
        description="The hostname or IP address of the outgoing SMTP relay.",
        title="Host",
        examples=["example.com"],
    )
    port: int = Field(
        ge=1,
        le=65536,
        description="The port of the outgoing SMTP relay.",
        title="Port",
        examples=[25, 587, 465],
    )
    user: str | None = Field(
        default=None,
        description="The user to authenticate with the SMTP relay as.",
        title="User",
        examples=["some_user"],
    )
    password: str | None = Field(
        default=None,
        description="SMTP password. Populated instead of password_id when secrets are not supported.",
        title="Password",
        examples=["somepasswd"],
    )
    password_id: str | None = Field(
        default=None,
        description="Juju secret ID for the SMTP password. Populated instead of password when secrets are supported.",
        title="Password ID",
        examples=["secret:123213123123123123123"],
    )
    auth_type: AuthType = Field(
        description="The type used to authenticate with the SMTP relay.",
        title="Auth type",
        examples=[AuthType.NONE],
    )
    transport_security: TransportSecurity = Field(
        description="The security protocol to use for the SMTP relay.",
        title="Transport security",
        examples=[TransportSecurity.NONE],
    )
    domain: str | None = Field(
        default=None,
        description="The MAIL FROM domain for the outgoing email.",
        title="Domain",
        examples=["example.com"],
    )
    skip_ssl_verify: bool = Field(
        default=False,
        description="Whether to skip verifying the SMTP relay's certificate. Written as `True` or `False`.",
        title="Skip SSL verify",
        examples=["False", "True"],
    )
    smtp_sender: str | None = Field(
        default=None,
        description="The email address to send notifications from.",
        title="SMTP sender",
        examples=["no-reply@example.com"],
    )
    recipients: Json[list[str]] | None = Field(
        default=None,
        description="The email addresses to send notifications to.",
        title="Recipients",
        examples=['["ops@example.com"]'],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
