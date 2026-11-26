# oauth

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST implement the OAuth 2.0 and OpenID Connect protocols, and MUST register a separate client for each relation.
- MUST write its endpoints, `issuer_url`, and `scope` to the application databag from the leader unit.
- MUST register the client with the requirer's configuration, and MUST update the client when the configuration changes.
- MUST put the client secret in a Juju secret, under the `secret` key, MUST grant the secret to the relation, and MUST write its ID as `client_secret_id`, along with `client_id`. Juju secrets need Juju 3 or later.
- SHOULD write `groups` if it has a claim with the user's groups.

### Requirer

- MUST write its client configuration to the application databag from the leader unit.
- If it uses the `authorization_code` grant type, MUST set `redirect_uri` to one or more redirect URIs that users can reach, which SHOULD use HTTPS.
- MUST only ask for grant types, scopes, and token endpoint authentication methods that the provider supports.
- MUST list any extra audiences that it needs for its tokens in `audience`.
- SHOULD treat the relation as not ready until the provider's application databag has `client_id` and `client_secret_id`.
- MUST read the client secret from the `secret` key of the Juju secret.
- SHOULD treat a missing `jwt_access_token` as `False`.
