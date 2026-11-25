"""This file defines the schemas for the provider and requirer sides of this relation interface."""

import json
from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, Json

CA_CERT = (
    "-----BEGIN CERTIFICATE-----\nMIIDPzCCAiegAwIBAgIUSV4nLL94rCgt...\n-----END CERTIFICATE-----\n"
)
CREDENTIALS = {
    "3081279da89c48a32923473c2c587019": "secret:cjk5slcrl3uc767oebp0",
    "b49e6098f245344f1035c3aa0e0c9181": "secret:cjk5slcrl3uc767oebpg",
}


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "vault_url": "https://10.152.183.104:8200",
                    "mount": "charm-barbican-secrets",
                    "ca_certificate": CA_CERT,
                    "credentials": json.dumps(CREDENTIALS),
                },
            ]
        }
    )

    vault_url: str = Field(
        description="The URL of the Vault server to connect to.",
        title="Vault URL",
        examples=["https://10.152.183.104:8200"],
    )
    mount: str = Field(
        description=(
            "The KV mount available for the requirer application, "
            "respecting the pattern 'charm-<requirer app>-<user provided suffix>'."
        ),
        title="Mount",
        examples=["charm-barbican-secrets"],
    )
    ca_certificate: str = Field(
        description="The CA certificate to use when validating the Vault server's certificate.",
        title="CA certificate",
        examples=[CA_CERT],
    )
    credentials: Json[Mapping[str, str]] = Field(
        description=(
            "A JSON object that maps each requirer unit's nonce to the ID of the Juju secret with that unit's credentials."
            " The secret has a 'role-id' and a 'role-secret-id'."
            " In case of wrap_ttl being requested, 'role-secret-id' will be empty and"
            " 'wrapping-token' will contain the role-secret-id as a response-wrapping token."
        ),
        title="Credentials",
        examples=[json.dumps(CREDENTIALS)],
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"mount_suffix": "secrets"},
                {"mount_suffix": "secrets", "wrap_ttl": "300"},
            ]
        }
    )

    mount_suffix: str = Field(
        description="Suffix to append to the mount name to get the KV mount.",
        title="Mount suffix",
        examples=["secrets"],
    )
    wrap_ttl: int | None = Field(
        default=None,
        title="Wrap TTL",
        description=(
            "Whether to request approle secret_id as a response-wrapping token with a certain TTL."
            " If not set, no wrapping will be made to secret_id. Otherwise, wrap_ttl specifies"
            " the duration of seconds before the expiration of the response-wrapping token."
        ),
        examples=["300"],
    )


class RequirerUnitData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"egress_subnet": "10.1.166.206/32", "nonce": "3081279da89c48a32923473c2c587019"},
                {
                    "egress_subnet": "10.1.166.230/32,10.1.1.0/32",
                    "nonce": "b49e6098f245344f1035c3aa0e0c9181",
                },
            ]
        }
    )

    egress_subnet: str = Field(
        description="A string of egress subnets separated by commas, in CIDR notation.",
        title="Egress subnet",
        examples=["10.1.166.206/32", "10.1.166.230/32,10.1.1.0/32"],
    )
    nonce: str = Field(
        description=(
            "Uniquely identifying value for this unit. `secrets.token_hex(16)` is recommended."
        ),
        title="Nonce",
        examples=["3081279da89c48a32923473c2c587019"],
    )


ProviderUnitData = None
