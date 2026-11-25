# s3

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the connection details to the application databag from the leader unit.
- Once the requirer has written `bucket`, MUST write `access-key` and `secret-key`, and SHOULD write `bucket`.
- MAY ignore the bucket that the requirer asks for, and provide a different one.
- If the S3 endpoint uses TLS with a custom CA, MUST write the complete CA chain to `tls-ca-chain`, one PEM certificate per string.
- SHOULD include any server-side encryption headers in `attributes`.
- MUST update the databag when the connection details change.

### Requirer

- MUST write `bucket` to the application databag from the leader unit when the relation is joined. If no bucket is configured, SHOULD generate a name, such as `relation-<relation ID>`.
- MUST use the bucket in the provider's databag, which might not be the one it asked for.
- SHOULD treat the relation as not ready until `access-key` and `secret-key` are both set.
- MUST allow other applications to use the same bucket.
- MUST relate to a different provider application for each bucket that it needs. Credentials belong to a relation, so different applications of the same charm can have different credentials.
