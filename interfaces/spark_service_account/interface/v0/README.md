# spark_service_account

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write to the application databag from the leader unit.
- Once the requirer has written `service-account`, MUST create that Kubernetes service account (and its namespace, if needed), unless `skip-creation` is `true`.
- Once the service account is ready, MUST write `service-account`, with the value that the requirer wrote.
- If the requirer lists `spark-properties` and `resource-manifest` in `requested-secrets`, MUST put the Spark properties for the service account (as a JSON object) under the `spark-properties` key of a Juju secret and the Kubernetes resource manifest (as YAML) under its `resource-manifest` key, write the secret's ID to `secret-extra`, and grant the secret to the relation. Otherwise, MAY write them in plain text, for requirers that don't support secrets.
- MUST update the secret's content when the Spark properties or the resource manifest change.
- Unless `skip-creation` is `true`, SHOULD delete the service account when the relation is removed.

### Requirer

- MUST write `service-account` to the application databag from the leader unit, with the namespace and the name of the service account, separated by a colon.
- MAY set `skip-creation` to `true` so that the provider doesn't create the service account.
- SHOULD NOT change `service-account` or `skip-creation` after writing them, since the provider only acts on them when `service-account` is first set.
- Unless Juju secrets aren't supported, MUST list `spark-properties` and `resource-manifest` in `requested-secrets`. Each entry in `requested-secrets` MUST be a valid Juju secret key (alphanumeric characters and dashes).
- SHOULD treat the relation as not ready until the provider has written `service-account`.
- MUST read the Spark properties and the resource manifest from the `secret-extra` secret, or from the databag if the provider wrote them there.
- SHOULD use the latest revision of the secret when it changes.
- SHOULD stop using the service account when the relation is removed.
