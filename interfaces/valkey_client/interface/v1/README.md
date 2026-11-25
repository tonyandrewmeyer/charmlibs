# valkey_client

## Behavior

Keywords are as in RFC 2119.

Both charms MUST support Juju secrets: sensitive fields are sent in Juju secrets rather than in the databag, with related fields grouped together in one secret. The library raises an error when the relation is initialised if either side doesn't support them.

### Provider

- MUST write to the application databag from the leader unit.
- MUST write `version` (`v1`) and, in `requests`, a response for each request, with the request's `resource`, `request-id`, and `salt`.
- MUST create a user and password for each request.
- MUST give that user read and write permissions on the keys and Pub/Sub channels that match the request's `resource`.
- MUST delete the user and its permissions when the relation is removed.
- MUST put the user's `username` and `password` in a Juju secret, and write the secret's ID to the response's `secret-user`.
- MUST write `endpoints`, a comma-separated list of all the read-write endpoints.
- MUST write `read-only-endpoints`, a comma-separated list of all the read-only endpoints.
- MUST write `sentinel-endpoints`, a comma-separated list of all the Valkey Sentinel endpoints, if Sentinel is available.
- MUST write `version`, the installed version of Valkey, in each response.
- MUST write `mode`, the high availability mode of Valkey (currently always `sentinel`).
- MUST put whether TLS is enabled (`true` or `false`) in `tls`, and the CA certificate of the server in `tls-ca` when it is, in a Juju secret, and write the secret's ID to the response's `secret-tls`.
- MUST update the responses when the endpoints, TLS details, or version change.

### Requirer

- MUST write `version` (`v1`) and, in `requests`, a JSON array with a request for each range of keys that it wants, from the leader unit.
- MUST set each request's `resource` to the keys and Pub/Sub channels that it wants to access, as a glob pattern (for example, `app:*`).
- MUST give each request a random `salt` and a `request-id` that is the first 16 characters of the SHA-256 hash of `<resource>:<salt>`, and MUST use the `request-id` to find the response to it.
- MUST NOT change a request's `resource`, `entity-type`, `extra-user-roles`, or `extra-group-roles` once the provider has seen it.

## v0 requirers

The provider also accepts a requirer that uses the v0 data_interfaces library, which writes the range of keys in `database`, along with `requested-secrets` and `provided-secrets`, and no `version`. The provider then writes a single response directly in the application databag: `database` (copied back), `endpoints`, `read-only-endpoints`, `sentinel_endpoints` (with an underscore), `mode`, `version`, `secret-user`, `secret-tls`, and `salt`.
