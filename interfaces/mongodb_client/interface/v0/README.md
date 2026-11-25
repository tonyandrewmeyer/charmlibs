# mongodb_client

## Behavior

Keywords are as in RFC 2119.

If both sides support Juju secrets, sensitive fields are sent in Juju secrets rather than in the databag, with related fields grouped together in one secret. If either side doesn't support Juju secrets, the provider writes those fields in the databag, under the same names as in the secret.

### Provider

- MUST write to the application databag from the leader unit.
- MUST create a relation user in the database cluster when the requirer writes `database`.
- MUST write `database` with the name of the database that was actually created.
- Unless the requirer writes `entity-type`, MUST put the relation user's credentials (`username`, `password`, and `uris`) in a Juju secret, write the secret's ID to `secret-user`, and grant the secret to the relation.
- If the requirer writes `entity-type`, MUST put the custom entity's credentials (`entity-name`, and `entity-password` if there is one) in a Juju secret, write the secret's ID to `secret-entity`, and grant the secret to the relation.
- SHOULD write `endpoints`, a comma-separated list of hosts that can be used to connect to the database. (A config server in a sharded cluster doesn't, because clients connect through mongos.)
- MUST write `replset`, the name of the replica set, when sharding is disabled, because clients need it to connect.
- SHOULD provide `uris`, a URI that can be passed to MongoDB client libraries as it is, so that clients don't need to build it.
- MAY write `version`, the version of the database engine.
- When TLS is enabled (such as with the [TLS Certificates Operator](https://github.com/canonical/tls-certificates-operator)), MUST put the CA chain in `tls-ca`, and `True` in `tls`, in a Juju secret, and write the secret's ID to `secret-tls`.
- If the requirer lists fields in `requested-secrets` other than those in the user, entity, and TLS secrets, MUST put those fields in another Juju secret and write its ID to `secret-extra`.
- MUST add the roles in `extra-user-roles` to the relation user, and the roles in `extra-group-roles` to the requested group.
- MUST allow more than one application to use the same database name.
- SHOULD remove the relation user when the relation is removed.
- MAY restrict where the relation user can connect from, unless the requirer sets `external-node-connectivity` to `true`.

### Requirer

- MUST write `requested-secrets`, a JSON array of the names of the fields that the provider should put in Juju secrets rather than in the databag. The names MUST be valid Juju secret keys (alphanumeric characters and dashes), and MUST include `username` and `password` (and `tls-ca` when TLS is enabled).
- MUST write the name of the database it wants in `database`.
- MUST use a different relation endpoint, with the same interface, for each database charm that it needs access to. Credentials belong to a relation, so different applications, even of the same charm, get different credentials.
- MAY write `extra-user-roles` (for example, `admin`), roles that the provider adds to the relation user.
- MAY write `extra-group-roles`, roles that the provider adds to the requested group.
- MAY write `entity-type` to ask for a custom entity instead of a relation user, and `entity-permissions` to set that entity's permissions.
- MAY set `external-node-connectivity` to `true` if it connects from outside the provider's network.
- MUST tolerate the provider ignoring the requested `database` in some cases, and MUST use the database name that the provider writes.
