# azure_service_principal

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `subscription-id` and `tenant-id` to the application databag from the leader unit.
- MUST put the client ID and client secret in a Juju secret, under the `client-id` and `client-secret` keys, and write the secret's ID to `secret-extra`. This applies whether or not the requirer lists them in `requested-secrets`.
- MUST grant the secret to the relation.
- MUST update the databag, or the secret's content, when the credentials change.

### Requirer

- MAY write `requested-secrets`. If it does, the list MUST include `client-id` and `client-secret`.
- MUST read the client ID and client secret from the secret in `secret-extra`.
- SHOULD treat the relation as not ready until the subscription ID, tenant ID, client ID, and client secret are all available.
- MUST use a different endpoint for each set of credentials that it needs. Credentials belong to a relation, so different applications of the same charm can have different credentials.
