# opensearch_client

## Behavior

Keywords are as in RFC 2119.

If both sides support Juju secrets, sensitive fields are sent in Juju secrets rather than in the databag, with related fields grouped together in one secret. If either side doesn't support Juju secrets, the provider writes those fields in the databag, under the same names as in the secret.

### Provider

- MUST write to the application databag from the leader unit.
- MUST create a relation user in the cluster when the requirer writes `index`.
  - MUST apply the permissions for the roles in `extra-user-roles` to this user (for example, `admin`). If `extra-user-roles` is empty, MUST apply a default role with read and write permissions on the index.
  - MUST remove this user when the relation is removed.
  - If more than one relation asks for the same index name, MUST let all of them access it.
- MAY create the requested index, but MUST NOT remove it when the relation is removed. Managing the index is the requirer's responsibility.
- MUST write `index` with the index that has been made available to the requirer.
- Unless the requirer writes `entity-type`, MUST put the relation user's credentials (`username` and `password`) in a Juju secret, write the secret's ID to `secret-user`, and grant the secret to the relation.
- If the requirer writes `entity-type`, MUST put the custom entity's credentials (`entity-name`, and `entity-password` if there is one) in a Juju secret, write the secret's ID to `secret-entity`, and grant the secret to the relation.
- MUST write `endpoints`, a comma-separated list of all the cluster endpoint addresses, and keep it up to date.
- MUST write `version`, the version of OpenSearch.
- When TLS is enabled (such as with the [TLS Certificates Operator](https://github.com/canonical/tls-certificates-operator)), MUST put the CA chain in `tls-ca` in a Juju secret, and write the secret's ID to `secret-tls`.
- If the requirer lists fields in `requested-secrets` other than those in the user, entity, and TLS secrets, MUST put those fields in another Juju secret and write its ID to `secret-extra`.

### Requirer

- MUST write `requested-secrets`, a JSON array of the names of the fields that the provider should put in Juju secrets rather than in the databag. The names MUST be valid Juju secret keys (alphanumeric characters and dashes), and MUST include `username` and `password` (and `tls-ca` when TLS is enabled).
- MUST write the name of the index it wants in `index`.
- MUST manage its own index, including creating and removing it. The `index` field is there so that the provider can give the relation user the right permissions on it.
- MUST use a different relation, with the same interface, for each index that it needs access to.
- MAY write roles for the relation user or requested entity in `extra-user-roles`. If it's empty, the provider applies a default role. The roles are:
  - `default`: read and write permissions on the index for this relation.
  - `admin`: control over the cluster, including creating new indices and setting cluster node roles.

  How these roles are implemented is up to the provider, since it varies slightly between applications that implement the OpenSearch API.
- MAY write `extra-group-roles`, roles that the provider applies to the requested group.
- MAY write `entity-type` to ask for a custom entity instead of an index user, and `entity-permissions` to set that entity's permissions.
- MUST tolerate the provider ignoring the requested `index` in some cases, and MUST use the index name that the provider writes.
