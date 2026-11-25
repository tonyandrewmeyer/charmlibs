# vault-autounseal

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write to the application databag from the leader unit.
- MUST create a `transit` backend to use for auto-unseal, if one does not already exist, and write its mount path as `mount_path`.
- MUST create an encryption key for the requirer in that backend, and write its name as `key_name`. The Vault charms name the key after the relation ID, so it is `charm-autounseal/keys/<relation ID>` in the `charm-autounseal` backend.
- MUST create a policy for the requirer that gives `update` capabilities on the encryption key.
- MUST create an AppRole for this policy, and a secret ID for the AppRole, and MUST store the role ID and the secret ID in a Juju secret, under the `role-id` and `secret-id` keys.
- SHOULD let the AppRole create periodic tokens, so that Vault can renew the token indefinitely.
- MUST grant the Juju secret to the relation, and write its ID as `credentials_secret_id`.
- MUST write the URL of the Vault server as `address`, and the CA certificate that the requirer should use to validate the server's certificate as `ca_certificate`.
- SHOULD create new credentials if the existing ones are no longer valid in Vault, for example after a snapshot restore.

### Requirer

- MUST NOT write to either databag.
- MUST retrieve the AppRole credentials (role ID and secret ID) from the Juju secret that the provider identified, and create a new token from them.
- MUST configure Vault with a `seal "transit"` stanza in which:
  - `address` is the provider's `address`.
  - `mount_path` is the provider's `mount_path`.
  - `key_name` is the provider's `key_name`.
  - The token is the one created from the AppRole credentials.
  - The CA certificate path points to a local copy of the provider's `ca_certificate`.

## Limitations

The interface only supports using the `transit` backend for auto-unseal. Other auto-unseal methods exist, but are not considered in this iteration, as they require external collaborators which fall outside of the charm ecosystem, and require the enterprise version of Vault.

Additionally, this version of the interface focuses purely on using the transit backend for auto-unseal, although there are other legitimate uses of using the transit backend. There may be a need for a more general-purpose `vault-transit` integration in the future.
