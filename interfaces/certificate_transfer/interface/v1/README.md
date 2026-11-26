# certificate_transfer

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the certificates to its application databag from the leader unit, with `version` set to `1`, if the requirer has written `version` as `1`. Otherwise, it SHOULD use version 0 of the interface.
- MUST update `certificates` when the set of certificates changes, and SHOULD write an empty list, rather than removing the field, when it has no certificates to share.

### Requirer

- MUST write `version` as `1` to its application databag from the leader unit when the relation is created.
- MUST use the provided certificates to authenticate TLS communications.
- SHOULD treat the certificates as an unordered set, so that a change in their order alone is not a change.
- SHOULD stop using the certificates from a relation when that relation is removed.
- MAY fall back to reading version 0 data from the provider's unit databag, for providers that don't support version 1.
