"""This file defines the schemas for the provider and requirer sides of this relation interface."""

from pydantic import BaseModel, ConfigDict, Field

CA_CERT = (
    "-----BEGIN CERTIFICATE-----\nMIIDTzCCAjegAwIBAgIUaM2XIUnDwnkc...\n-----END CERTIFICATE-----\n"
)


class ProviderAppData(BaseModel):
    """Provider side of the vault-autounseal relation interface."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "address": "https://10.152.183.217:8200",
                    "mount_path": "charm-autounseal",
                    "key_name": "2",
                    "credentials_secret_id": "secret://575cd150-f7c2-4710-88a3-3f33e14e867c/copsdgnmp25c77tkgke0",
                    "ca_certificate": CA_CERT,
                },
            ]
        }
    )

    address: str = Field(
        description="The address of the Vault server to connect to.",
        title="Address",
        examples=["https://10.152.183.217:8200"],
    )
    mount_path: str = Field(
        description="The path to the transit engine mount point where the autounseal keys are stored.",
        title="Mount path",
        examples=["charm-autounseal"],
    )
    key_name: str = Field(
        description="The name of the key to use for autounseal.",
        title="Key name",
        examples=["2"],
    )
    credentials_secret_id: str = Field(
        description=(
            "The secret id of the Juju secret which stores the credentials for authenticating with the Vault server."
            " The secret has a `role-id` and a `secret-id`."
        ),
        title="Credentials secret ID",
        examples=["secret://575cd150-f7c2-4710-88a3-3f33e14e867c/copsdgnmp25c77tkgke0"],
    )
    ca_certificate: str = Field(
        description="The CA certificate to use when validating the Vault server's certificate.",
        title="CA certificate",
        examples=[CA_CERT],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
