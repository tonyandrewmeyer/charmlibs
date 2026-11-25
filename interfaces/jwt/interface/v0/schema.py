"""This file defines the schema for the provider side of the jwt interface."""

from pydantic import BaseModel, ConfigDict, Field


class _BareStringDatabag(BaseModel):
    """Base class for databag models that don't strictly JSON encode all entries."""

    @staticmethod
    def __juju_decoder__(value: str) -> str:
        """Pass Juju's string through unmodified to be decoded by individual field validators."""
        return value

    @staticmethod
    def __juju_encoder__(value: str | None) -> str:
        """Convert `None` to "", erasing the value; Ops will error on a non-string."""
        return "" if value is None else value


class ProviderAppData(_BareStringDatabag):
    """The JWT validation settings."""

    model_config = ConfigDict(
        strict=True,
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "secret-extra": "secret://91f805c5-5b49-47a3-8e7b-70befa766caf/cuni0uh34trs5tihuf9g",
                    "roles-key": "roles",
                    "jwt-header": "Authorization",
                    "jwt-url-parameter": "jwt",
                    "subject-key": "userid",
                    "required-audience": "opensearch",
                    "required-issuer": "my-identity-provider",
                    "jwt-clock-skew-tolerance": "60",
                },
                {
                    "secret-extra": "secret://91f805c5-5b49-47a3-8e7b-70befa766caf/cuni0uh34trs5tihuf9g",
                    "roles-key": "roles",
                },
            ]
        },
    )

    secret_extra: str = Field(
        alias="secret-extra",
        description=(
            "A Juju secret ID that points to a secret containing signing-key, the key or keys"
            " used to verify the token. Multiple keys can be given as a comma-separated list."
        ),
        examples=["secret://91f805c5-5b49-47a3-8e7b-70befa766caf/cuni0uh34trs5tihuf9g"],
        title="Signing key secret ID",
    )

    roles_key: str = Field(
        alias="roles-key",
        description="The key in the JSON payload that stores the user's roles.",
        examples=["roles"],
        title="Roles key",
    )

    jwt_header: str | None = Field(
        default=None,
        alias="jwt-header",
        description="The HTTP header in which the token is transmitted (typically the Authorization header).",
        examples=["Authorization"],
        title="JWT header",
    )

    jwt_url_parameter: str | None = Field(
        default=None,
        alias="jwt-url-parameter",
        description="The HTTP URL parameter that has the token, if it's not in jwt-header.",
        examples=["jwt"],
        title="JWT URL parameter",
    )

    subject_key: str | None = Field(
        default=None,
        alias="subject-key",
        description="The key in the JSON payload that stores the username.",
        examples=["user"],
        title="Subject key",
    )

    required_audience: str | None = Field(
        default=None,
        alias="required-audience",
        description="The name of the audience that the JWT must specify. Corresponds to the `aud` claim of the JWT.",
        examples=["opensearch", "project-1"],
        title="Required audience",
    )

    required_issuer: str | None = Field(
        default=None,
        alias="required-issuer",
        description="The issuer that the JWT must specify. Corresponds to the `iss` claim of the JWT.",
        examples=["my-identity-provider"],
        title="Required issuer",
    )

    jwt_clock_skew_tolerance: str | None = Field(
        default=None,
        alias="jwt-clock-skew-tolerance",
        description=(
            "Time in seconds that is tolerated as clock disparity between the authentication"
            " parties. A decimal string."
        ),
        examples=["30"],
        title="JWT clock skew tolerance",
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
