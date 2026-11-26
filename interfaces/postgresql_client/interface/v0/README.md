# postgresql_client

## Behavior

Keywords are as in RFC 2119.

If both sides support Juju secrets, sensitive fields are sent in Juju secrets rather than in the databag, with related fields grouped together in one secret. If either side doesn't support Juju secrets, the provider writes those fields in the databag, under the same names as in the secret.

### Provider

- MUST write to the application databag from the leader unit, except for `state`, which each unit writes to its own databag.
- MUST create a relation user in the database cluster when the requirer writes `database`.
- MUST put the relation user's credentials (`username` and `password`) in a Juju secret, write the secret's ID to `secret-user`, and grant the secret to the relation.
- MUST write `database` with the name of the database that was actually created, or the prefix that the requirer asked for.
- MUST write `endpoints`, the address of the primary, which can be used for read/write queries.
- SHOULD write `read-only-endpoints`, a comma-separated list of hosts or one Kubernetes service, which can be used for read-only queries.
- MUST write `uris`, a connection string in libpq's URI format that can be used to connect directly to the database, unless the requirer asked for a prefix that no database matches. If the requirer lists `uris` in `requested-secrets`, it goes in the same secret as the credentials.
- If the requirer lists `read-only-uris` in `requested-secrets`, MUST put a connection string for the read-only endpoints, in libpq's URI format, in the same secret as the credentials.
- MAY write `version`, the version of the database engine.
- SHOULD write `tls`, `True` or `False`, to say whether TLS is enabled.
- When TLS is enabled (such as with the [TLS Certificates Operator](https://github.com/canonical/tls-certificates-operator)), SHOULD write the CA chain in `tls-ca`. If the requirer lists `tls` or `tls-ca` in `requested-secrets`, those go in a Juju secret, whose ID the provider writes to `secret-tls`.
- If the requirer lists fields in `requested-secrets` other than those in the user and TLS secrets, MUST put those fields in another Juju secret and write its ID to `secret-extra`.
- MUST add the roles in `extra-user-roles` to the relation user. If a requested role isn't valid, SHOULD set a blocked status.
- MAY use the name and password in `requested-entity-secret` for the relation user, instead of generating them. If a user with that name already exists, MUST NOT reuse it, and SHOULD set a blocked status.
- If it supports prefix requests and the requirer asks for one, MUST give the relation user access to every database that matches the prefix, and write their names to `prefix-databases`.
- MUST allow more than one application to use the same database name.
- SHOULD remove the relation user when the relation is removed.
- MAY make the endpoints reachable only from the requirer's host, unless the requirer sets `external-node-connectivity` to `true`. When the requirer sets it, the endpoints MUST be reachable from other hosts. PgBouncer on machines offers `localhost` or a Unix socket unless the requirer sets it.
- MAY set `subordinated` to `true` if it needs time to start serving when the requirer scales up. If it does, each of its units MUST set `state` to `ready` in its unit databag when it is ready to serve.

### Requirer

- MUST write `requested-secrets`, a JSON array of the names of the fields that the provider should put in Juju secrets rather than in the databag. The names MUST be valid Juju secret keys (alphanumeric characters and dashes), and MUST include `username` and `password` (and `tls-ca` when TLS is enabled).
- MUST write `database`: either the name of the database it wants, or a prefix, which is at least three characters followed by `*`.
- MUST use a different relation endpoint, with the same interface, for each database charm that it needs access to. Credentials belong to a relation, so different applications, even of the same charm, get different credentials.
- MAY write `extra-user-roles`, roles that the provider adds to the relation user.
- MAY write `extra-group-roles`, roles that the provider adds to the requested group.
- MAY write `entity-type` to ask for a custom entity instead of a relation user, and `entity-permissions` to set that entity's permissions. None of the PostgreSQL charms create custom entities yet.
- MAY write `requested-entity-secret`, the ID of a Juju secret, granted to the relation, with the name (under `entity-name`) and optionally the password (under `password`) that it wants for its user. MUST handle the provider not using them.
- MAY write `prefix-matching` when it asks for a prefix. The PostgreSQL charms only support `all`.
- MAY set `external-node-connectivity` to `true` if it connects from outside its own host.
- MUST tolerate the provider ignoring the requested `database` in some cases, and MUST use the database name that the provider writes.
- When the provider sets `subordinated` to `true`, MUST NOT use the relation until the provider unit's `state` is `ready`.
