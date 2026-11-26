"""This file defines the schemas for the provider and requirer sides of the `kratos_info` interface."""

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "admin_endpoint": "http://kratos.mymodel.svc.cluster.local:4434",
                    "public_endpoint": "http://kratos.mymodel.svc.cluster.local:4433",
                    "login_browser_endpoint": "https://example.com/mymodel-kratos/self-service/login/browser",
                    "sessions_endpoint": "http://kratos.mymodel.svc.cluster.local:4433/sessions/whoami",
                    "providers_configmap_name": "oidc-providers",
                    "schemas_configmap_name": "identity-schemas",
                    "configmaps_namespace": "mymodel",
                    "mfa_enabled": "False",
                    "oidc_webauthn_sequencing_enabled": "True",
                    "verification_enabled": "False",
                    "feature_flags": "password,webauthn,totp,backup_codes",
                },
                {
                    "admin_endpoint": "http://10.64.140.44/testing-kratos",
                    "public_endpoint": "http://10.64.140.45/testing-kratos",
                    "login_browser_endpoint": "http://10.64.140.45/testing-kratos/self-service/login/browser",
                    "sessions_endpoint": "http://10.64.140.45/testing-kratos/sessions/whoami",
                    "providers_configmap_name": "oidc-providers",
                    "schemas_configmap_name": "identity-schemas",
                    "configmaps_namespace": "testing",
                    "mfa_enabled": "True",
                    "oidc_webauthn_sequencing_enabled": "False",
                    "verification_enabled": "True",
                    "privileged_session_max_age": "15m",
                },
            ]
        }
    )

    admin_endpoint: AnyHttpUrl = Field(
        description="The URL of the Kratos admin API.",
        examples=["http://kratos.mymodel.svc.cluster.local:4434"],
    )
    public_endpoint: AnyHttpUrl = Field(
        description="The URL of the Kratos public API.",
        examples=["http://kratos.mymodel.svc.cluster.local:4433"],
    )
    login_browser_endpoint: AnyHttpUrl = Field(
        description="The Kratos endpoint that starts a browser-based login flow. This is based on the externally accessible URL of Kratos, rather than on `public_endpoint`.",
        examples=["https://example.com/mymodel-kratos/self-service/login/browser"],
    )
    sessions_endpoint: AnyHttpUrl = Field(
        description="The Kratos endpoint that says who the current session belongs to.",
        examples=["http://kratos.mymodel.svc.cluster.local:4433/sessions/whoami"],
    )
    providers_configmap_name: str = Field(
        description="The name of the Kubernetes ConfigMap that holds the configuration of the identity providers.",
        examples=["oidc-providers"],
    )
    schemas_configmap_name: str = Field(
        description="The name of the Kubernetes ConfigMap that holds the identity schemas.",
        examples=["identity-schemas"],
    )
    configmaps_namespace: str = Field(
        description="The Kubernetes namespace of the ConfigMaps.",
        examples=["mymodel"],
    )
    mfa_enabled: bool = Field(
        description="Whether users must set up and use multi-factor authentication. Written as `True` or `False`.",
        examples=["False", "True"],
    )
    oidc_webauthn_sequencing_enabled: bool = Field(
        description="Whether users must set up a WebAuthn key after logging in with an external identity provider. Written as `True` or `False`.",
        examples=["False", "True"],
    )
    verification_enabled: bool | None = Field(
        default=None,
        description="Whether users must verify their accounts. Written as `True` or `False`.",
        examples=["False", "True"],
    )
    feature_flags: str | None = Field(
        default=None,
        description="The Kratos features that are enabled, separated by commas.",
        examples=["password,webauthn,totp,backup_codes", "password,account_linking"],
    )
    privileged_session_max_age: str | None = Field(
        default=None,
        description="The maximum age of a privileged Kratos session, as a duration.",
        examples=["15m"],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
