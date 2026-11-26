# vault-kv

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write to the application databag from the leader unit.
- MUST write the URL of the Vault server, and a CA certificate that can validate the server's certificate.
- MUST create a KV mount for the requirer, named `charm-<requirer app>-<mount_suffix>`, and write its name as `mount`.
- MUST create an AppRole for each requirer unit, restricted to that unit's egress subnets.
- MUST create a Juju secret for each requirer unit that contains a `role-id` and a `role-secret-id`, MUST grant it to the relation, and MUST write the secret's ID in `credentials`, under the unit's nonce.
- If the requirer sets `wrap_ttl`, MUST put a response-wrapping token in the secret instead of the `role-secret-id`. The token MUST contain the response of the `POST /auth/approle/role/:role_name/secret-id` API call. See the Vault documentation on [response wrapping](https://developer.hashicorp.com/vault/docs/concepts/response-wrapping).
- MAY have out-of-date credentials for a unit for some time after the unit's identity changes, for example during an upgrade, until it has generated new ones.
- SHOULD remove the credentials of units that have left the relation.

### Requirer

- MUST write a mount suffix to the application databag from the leader unit.
- MUST write the unit's egress subnets to each unit's databag, as a comma-separated list in CIDR notation. The provider uses them to restrict access to the KV mount.
- MUST write a nonce, a string that uniquely identifies the unit, to each unit's databag.
- MUST write the new egress subnets when a unit's egress subnets change, so that the provider can generate new credentials.
- MAY write a `wrap_ttl`, to get the `role-secret-id` as a response-wrapping token with that TTL.
