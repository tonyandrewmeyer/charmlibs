# smtp

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the SMTP details to the application databag from the leader unit.
- MUST NOT set both `password` and `password_id`.
- SHOULD use `password_id` rather than `password`, unless secrets are not supported.
- If it sets `password_id`, MUST use a Juju secret that has the password under the `password` key.
- If it owns that secret, MUST grant it to the relation, and SHOULD revoke the grant when the relation is removed.
- MUST update the databag when the SMTP details change.

### Requirer

- MUST NOT write to either databag.
- SHOULD treat the relation as not ready until the provider's application databag is populated.
- If `password_id` is set, MUST read the password from the `password` key of that secret.
- SHOULD use the latest revision of the secret when it changes.
