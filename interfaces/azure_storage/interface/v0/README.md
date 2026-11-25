# azure_storage

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `version` (currently `1`) to the application databag when the relation is created, and MUST NOT write anything else until the requirer has written `version` or `container`.
- MUST write the connection details, including `container`, `storage-account`, and `connection-protocol`, to the application databag from the leader unit.
- If the requirer lists `secret-key` in `requested-secrets`, MUST put the storage account key in a Juju secret, under the `secret-key` key, write the secret's ID to `secret-extra`, and grant the secret to the relation. Otherwise, MAY write the key to `secret-key` in plain text, for requirers that don't support secrets.
- MAY ignore the `container` that the requirer asks for, and provide a different one.
- MAY expect the container to exist already, rather than creating it when the relation is joined.
- MUST update the databag, or the secret's content, when the connection details or the key change.

### Requirer

- MUST write `version` (currently `1`) to the application databag from the leader unit when the relation is joined.
- MAY write `container` to ask for a specific container. If the provider has written data without `version` (an older provider), MUST write `container`, using `relation-<relation ID>` if it has no name to ask for.
- SHOULD list `secret-key` in `requested-secrets`.
- MUST use the container in the provider's databag, which might not be the one it asked for.
- SHOULD treat the relation as not ready until `container`, `storage-account`, `connection-protocol`, and the storage account key are all available.
- MUST allow other applications to use the same container.
- MUST use a different endpoint for each container that it needs. Credentials belong to a relation, so different applications of the same charm can have different credentials.
