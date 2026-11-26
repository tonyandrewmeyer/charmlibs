# openfga

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `grpc_api_url` and `http_api_url` to the application databag from the leader unit, and MUST update them when they change.
- MUST create an authorization store in OpenFGA when the requirer provides `store_name`, and MUST then write its ID as `store_id`. MAY use an existing store with the same name.
- MUST put the preshared token in a Juju secret, under the `token` key, MUST grant the secret to the relation, and MUST write its ID as `token_secret_id`.
- SHOULD NOT write `token`.

### Requirer

- MUST write `store_name` to the application databag from the leader unit.
- SHOULD treat the store as not ready until the provider's application databag has `store_id` and `token_secret_id` or `token`.
- MUST use `store_id`, the URLs, and the token to set up an OpenFGA connection, and MUST read the token from the `token` key of the Juju secret.
- MAY use `token` if the provider doesn't set `token_secret_id`.
