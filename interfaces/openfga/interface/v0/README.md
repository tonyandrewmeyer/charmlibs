# openfga

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the address, scheme, and port of the OpenFGA service to the application databag from the leader unit, and MUST update them when they change.
- MUST create an authorization store in OpenFGA when the requirer provides `store_name`, and MUST then write its ID as `store_id`.
- If Juju secrets are available, MUST put the preshared token in a Juju secret, under the `token` key, and MUST write its ID as `token_secret_id`. Otherwise, MUST write the token as `token`.

### Requirer

- MUST write `store_name` to the application databag from the leader unit.
- MUST use `store_id`, the address, scheme, and port, and the token to set up an OpenFGA connection.
