# kratos_external_idp

## Direction

An administrator creates client credentials for Kratos on the external identity provider, and gives them to the provider charm, usually as configuration. The provider passes them to Kratos in the relation. Kratos then writes the redirect URI and the ID that it uses for the identity provider, and the administrator registers the redirect URI on the external identity provider.

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the configuration of one or more identity providers to the application databag from the leader unit.
- MUST set `secret_backend` to `relation`, since the `secret` and `vault` backends aren't implemented.
- If `provider` is `generic` or `auth0`, MUST set `client_secret` and `issuer_url`.
- If `provider` is `microsoft`, MUST set `client_secret` and `tenant_id`.
- If `provider` is `apple`, MUST set `team_id`, `private_key_id`, and `private_key`, and doesn't need to set `client_secret`.
- For any other `provider`, MUST set `client_secret`.
- MUST NOT set the provider-specific fields of a different provider. Fields that don't apply can be left out, rather than set to null.
- MUST update the databag when the configuration changes, and SHOULD clear it when the identity provider is disabled.

### Requirer

- MUST write a `redirect_uri` and a `provider_id` for each identity provider in the provider's databag to the application databag from the leader unit.
- If the provider set a `provider_id`, MUST use the same ID.
- SHOULD NOT write anything until it has an externally accessible URL, since the redirect URI is based on it.
- SHOULD stop using the identity provider, and clear the application databag, when the provider's databag is cleared or the relation is removed.
