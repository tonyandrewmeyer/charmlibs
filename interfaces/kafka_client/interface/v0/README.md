# kafka_client

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write to the application databag from the leader unit.
- MUST create a SASL/SCRAM user for each relation once the requirer has written `topic`, and MUST NOT write the credentials until the user exists.
- MUST grant the user ACLs for the roles in `extra-user-roles`. The `producer` role gets `WRITE`, `DESCRIBE`, and `CREATE` on the topic. The `consumer` role gets `READ` and `DESCRIBE` on the topic, and `READ` on the consumer groups that start with `consumer-group-prefix`. The `admin` role makes the user a super-user. The `manager` role gets every operation on every topic, group, and transactional ID.
- SHOULD grant the user the permissions in `entity-permissions`, as well as those from its roles.
- If the requirer writes `entity-type`, SHOULD create a custom entity with `entity-name` and `entity-password`, and MUST delete it when the relation is removed.
- MUST delete the user and its ACLs from the Kafka cluster when the relation is removed.
- MAY give the requirer a different topic from the one it asked for.
- If the requirer lists the credentials in `requested-secrets`, MUST put them in a Juju secret, under the `username` and `password` keys, write the secret's ID to `secret-user`, and grant the secret to the relation. Otherwise, MAY write them to `username` and `password` in plain text, for requirers that don't support secrets.
- MUST write `tls` as `enabled` or `disabled`, and SHOULD provide the CA chain in `tls-ca` when TLS is enabled, in the `secret-tls` secret if the requirer lists it in `requested-secrets`.
- If `extra-user-roles` includes `consumer`, MAY write `consumer-group-prefix`.
- MAY write `zookeeper-uris`, for admin clients that need to reach ZooKeeper directly.
- If the requirer provides `mtls-cert`, MAY also authenticate the requirer by that certificate, granting the same ACLs to the certificate's principal. This needs TLS on the provider.
- MUST update the databag, or the secrets' content, when the endpoints, credentials, or TLS settings change.

### Requirer

- MUST write `topic` to the application databag from the leader unit.
- SHOULD write `extra-user-roles`, with the roles that it needs.
- MAY write `consumer-group-prefix`, `extra-group-roles`, `entity-type`, and `entity-permissions`.
- MUST NOT change `entity-type`, `extra-user-roles`, or `extra-group-roles` once the provider has responded.
- SHOULD list `username`, `password`, `tls`, and `tls-ca` in `requested-secrets`.
- MUST use the topic in the provider's databag, which might not be the one it asked for.
- SHOULD treat the relation as not ready until the endpoints and credentials are all available.
