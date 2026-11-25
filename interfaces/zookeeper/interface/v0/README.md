# zookeeper

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write to the application databag from the leader unit.
- MUST create a user for each relation once the requirer has written `database`, with the ACL permissions in `extra-user-roles` on that zNode. If the requirer doesn't write `extra-user-roles`, the user gets `cdrwa`.
- MUST set up the ACLs before writing the credentials.
- SHOULD accept `chroot` as an older name for `database`, and MAY write `chroot` as a copy of `database` for older requirers.
- MAY give the requirer a different zNode from the one it asked for.
- If the requirer lists the credentials in `requested-secrets`, MUST put `username`, `password`, and `uris` in a Juju secret, write the secret's ID to `secret-user`, and grant the secret to the relation. Otherwise, MAY write them in plain text, for requirers that don't support secrets.
- MUST write `tls` as `enabled` or `disabled`, in the `secret-tls` secret if the requirer lists it in `requested-secrets`. When TLS is enabled, SHOULD also provide the CA chain under the `tls-ca` key of that secret.
- If the requirer lists other fields in `requested-secrets`, MUST put them in a Juju secret and write its ID to `secret-extra`.
- MAY write `version`, with the ZooKeeper version.
- SHOULD remove the user's ACLs when the relation is removed.
- MUST update the databag, or the secrets' content, when the endpoints, credentials, or TLS settings change.

### Requirer

- MUST write `database` to the application databag from the leader unit.
- SHOULD list `username`, `password`, `tls`, `tls-ca`, and `uris` in `requested-secrets`. If it writes `requested-secrets`, it MUST include `username` and `password`.
- MAY write `extra-user-roles`, with the ACL permissions that it needs.
- MUST use the zNode in the provider's databag, which might not be the one it asked for.
- MUST allow other applications to use the same zNode.
- MUST use a different endpoint for each ZooKeeper cluster that it needs. Credentials belong to a relation, so different applications of the same charm have different credentials.
