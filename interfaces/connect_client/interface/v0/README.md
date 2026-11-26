# connect_client

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write to the application databag from the leader unit.
- MUST download the plugin tarball from `plugin-url` and make the plugins available on every Kafka Connect worker. If `plugin-url` is `NOT-REQUIRED`, MUST skip this step.
- MUST create a user for the Kafka Connect REST interface for each relation once the plugins are available on every worker, and MUST NOT write the credentials before then.
- If the requirer lists the credentials in `requested-secrets`, MUST put them in a Juju secret, under the `username` and `password` keys, write the secret's ID to `secret-user`, and grant the secret to the relation. Otherwise, MAY write them to `username` and `password` in plain text, for requirers that don't support secrets.
- If the REST endpoints use HTTPS, SHOULD put the CA chain in a Juju secret, under the `tls-ca` key, and write the secret's ID to `secret-tls`.
- MUST delete the user, and clean up the requirer's plugin files, when the relation is removed.
- SHOULD delete the requirer's connectors when the relation is removed.

### Requirer

- MUST write `plugin-url` to the application databag from the leader unit: either the URL of a single tarball with all the plugin files, which MUST be reachable from the provider, or `NOT-REQUIRED` if it doesn't need a plugin.
- SHOULD list `username`, `password`, and `tls-ca` in `requested-secrets`.
- MUST manage the lifecycle of its own connectors and tasks through the Kafka Connect REST endpoints, using the credentials from the provider.
