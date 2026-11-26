# certificate_transfer

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write a public certificate, a CA certificate, a CA chain, or any combination of them, to its unit databag.
- SHOULD write `version` as `0`.
- MUST update the unit databag when the certificates change, and SHOULD remove `certificate`, `ca`, and `chain` when it no longer has certificates to share.
- SHOULD use version 1 of the interface instead if the requirer writes `version` as `1`.

### Requirer

- MUST write the version of the interface that it supports, `0`, as `version` in its application databag, from the leader unit.
- MUST use the provided certificate, CA certificate, and chain to authenticate TLS communications.
- SHOULD accept `certificate` and `ca` either as plain PEM strings or as JSON-encoded strings, because providers that use version 1 of the library write them JSON-encoded.
