# jwt

## Behavior

Keywords are as in RFC 2119.

Both charms MUST run on Juju 3 or later, so that they can use Juju secrets.

### Provider

- MUST write the settings to the application databag from the leader unit.
- MUST always provide the signing key and `roles-key`, and MUST NOT write anything until both are set.
- MUST provide each of the optional settings (`jwt-header`, `jwt-url-parameter`, `subject-key`, `required-audience`, `required-issuer`, and `jwt-clock-skew-tolerance`) that has a value, and only those.
- MUST put the signing key in a Juju secret, under the `signing-key` key, write the secret's ID to `secret-extra`, and grant the secret to the relation.
- MUST put everything other than the signing key in the databag.
- MUST update the databag, or the secret's content, when the settings change.

### Requirer

- MUST NOT write to either databag.
- MUST read the signing key from the `signing-key` key of the secret in `secret-extra`.
- MUST use all the settings that the provider gives.
- SHOULD apply the new signing key when the secret changes.
