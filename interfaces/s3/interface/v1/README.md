# s3

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `version` (currently `1`) to the application databag when the relation is created, and MUST NOT write anything else until the requirer has written `version` or `bucket`.
- MUST write the connection details to the application databag from the leader unit.
- If the requirer lists `access-key` and `secret-key` in `requested-secrets`, MUST put them in a Juju secret, under the `access-key` and `secret-key` keys, write the secret's ID to `secret-extra`, and grant the secret to the relation. Otherwise, MAY write them in plain text, for requirers using `v0` of the interface.
- If the requirer doesn't write `requested-secrets` (a requirer using `v0`), MUST ignore its `bucket`, which the `v0` library always fills in.
- If a bucket is requested, by the requirer or in the provider's own configuration, MUST create it in the object storage if it doesn't exist, and MUST write `bucket` once the bucket is available.
- MAY ignore the `bucket` and `path` that the requirer asks for, and provide different ones.
- If the S3 endpoint uses TLS with a custom CA, MUST write the complete CA chain to `tls-ca-chain`, one PEM certificate per string.
- SHOULD include any server-side encryption headers in `attributes`.
- MUST update the databag, or the secret's content, when the connection details or the credentials change.

### Requirer

- MUST write `version` (currently `1`) and `requested-secrets` (`["access-key", "secret-key"]`) to the application databag from the leader unit when the relation is joined.
- MAY write `bucket` and `path` to ask for a specific bucket and path. If the provider has written data without `version` (a provider using `v0`), MUST write `bucket`, using `relation-<relation ID>` if it has no name to ask for.
- MUST read `access-key` and `secret-key` from the secret in `secret-extra`, or from the databag if the provider wrote them there.
- MUST use the bucket and path in the provider's databag, which might not be the ones it asked for.
- SHOULD treat the relation as not ready until `access-key` and `secret-key` are both available.
- MUST allow other applications to use the same bucket.
- If it needs access to more than one bucket, MUST use a different endpoint for each bucket when the provider honours its requests. If the provider ignores its requests, MUST relate to a different provider application for each bucket instead.

## What's different from `v0`?

* `v1` puts `access-key` and `secret-key` in a Juju secret, and shares the secret's ID in `secret-extra`, where `v0` shares them in plain text in the relation databag.
* Both sides of `v1` share a `version` field, the version of the relation data schema, so that each side can tell which version the other is using and change its behaviour if it needs to. Older `v1` libraries shared `lib-version` instead, in the format `{LIBAPI}.{LIBPATCH}`.

## Migration strategy

To move a charm from `v0` to `v1` of the interface, switch from the `charms.data_platform_libs.s3` charm library to `object-storage-charmlib`. The new library still supports charms using `v0` of the interface, but the relation needs to be removed and created again to start using `v1`.

The `s3-integrator` charm in track `1` is built on Ubuntu 22.04, and the charm in track `2`, which uses `v1`, is built on Ubuntu 24.04, so you can't refresh from one to the other in place.
