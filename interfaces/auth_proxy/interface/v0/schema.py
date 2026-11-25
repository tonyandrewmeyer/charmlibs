"""This file defines the schemas for the provider and requirer sides of the `auth_proxy` interface."""

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, Json


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "protected_urls": '["https://10.64.140.43/model-myapp", "https://ingress.example.com/model-myapp"]',
                    "headers": '["X-Auth-Request-User", "X-Auth-Request-Email"]',
                    "allowed_endpoints": '["welcome", "about/app"]',
                    "authenticated_emails": '["alice@example.com"]',
                    "authenticated_email_domains": '["example.com"]',
                    "app_name": "myapp",
                },
                {
                    "protected_urls": '["https://ingress.example.com/model-myapp"]',
                    "headers": '["X-User"]',
                    "allowed_endpoints": "[]",
                },
            ]
        }
    )

    protected_urls: Json[list[AnyHttpUrl]] = Field(
        description="The externally accessible URLs of the requirer (its ingress URLs) that the Identity and Access Proxy protects, as a JSON list.",
        examples=['["https://ingress.example.com/model-myapp"]', "[]"],
    )
    allowed_endpoints: Json[list[str]] = Field(
        description="The paths under the protected URLs that don't need authentication, as a JSON list.",
        examples=['["welcome", "about/app"]', "[]"],
    )
    headers: Json[list[str]] = Field(
        description="The headers to set on requests after a successful authentication, as a JSON list. Which headers are supported depends on the provider: `oauth2-proxy-k8s` supports `X-Auth-Request-User`, `X-Auth-Request-Groups`, `X-Auth-Request-Email`, and `X-Auth-Request-Preferred-Username`, and `oathkeeper` supports `X-User`, `X-Email`, and `X-Name`.",
        examples=['["X-Auth-Request-User", "X-Auth-Request-Email"]', '["X-User"]', "[]"],
    )
    authenticated_emails: Json[list[str]] | None = Field(
        default=None,
        description="The email addresses of the users that are allowed access, as a JSON list.",
        examples=['["alice@example.com"]', "[]"],
    )
    authenticated_email_domains: Json[list[str]] | None = Field(
        default=None,
        description="The email domains of the users that are allowed access, as a JSON list.",
        examples=['["example.com"]', "[]"],
    )
    app_name: str | None = Field(
        default=None,
        description="The name of the requirer application.",
        examples=["myapp"],
    )


ProviderAppData = None
ProviderUnitData = None
RequirerUnitData = None
