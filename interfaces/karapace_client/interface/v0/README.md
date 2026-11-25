# karapace_client

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write to the application databag from the leader unit.
- SHOULD wait for the requirer to write `subject` before doing anything else.
- MUST create a Karapace user for each relation once the requirer has written `subject`.
- MUST give the user the access for its role: with `user`, read access to the subjects whose names start with `subject`; with `admin`, full access to every subject. A requirer that doesn't write `extra-user-roles` gets the `user` role.
- MAY create the requested subject if it doesn't exist.
- If the requirer writes `entity-type`, SHOULD create a custom entity with `entity-name` and `entity-password`, and MUST delete it when the relation is removed.
- MUST delete the user from Karapace when the relation is removed.
- If the requirer lists the credentials in `requested-secrets`, MUST put them in a Juju secret, under the `username` and `password` keys, write the secret's ID to `secret-user`, and grant the secret to the relation. Otherwise, MAY write them to `username` and `password` in plain text, for requirers that don't support secrets.
- SHOULD write `tls` as `enabled` or `disabled`, in the `secret-tls` secret if the requirer lists it in `requested-secrets`.
- MUST update the databag, or the secrets' content, when the endpoints or credentials change.

### Requirer

- MUST write `subject` to the application databag from the leader unit.
- MAY write `extra-user-roles`, as either `admin` or `user`.
- MAY write `extra-group-roles`, `entity-type`, and `entity-permissions`.
- MUST NOT change `entity-type`, `extra-user-roles`, or `extra-group-roles` once the provider has responded.
- SHOULD list `username`, `password`, and `tls` in `requested-secrets`.
- SHOULD treat the relation as not ready until the endpoints and credentials are all available, and then use them to configure its Karapace clients.
