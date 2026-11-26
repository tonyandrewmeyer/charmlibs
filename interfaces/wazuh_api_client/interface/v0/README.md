# wazuh_api_client

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the application databag from the leader unit.
- MUST put the API credentials in a Juju secret that it owns, with the user under the `user` key and the password under the `password` key, and MUST NOT put them in the databag.
- MUST grant that secret to the relation.
- MUST update the secret's content when the credentials change, and MUST update the databag when the endpoint changes.

### Requirer

- MUST NOT write to either databag.
- SHOULD treat the relation as not ready until both fields are set, the endpoint is a valid URL, and the secret can be read and has non-empty `user` and `password` values.
- MUST read the user and password from the same revision of the secret.
- SHOULD observe `secret-changed` for that secret and use the latest revision, since rotating the credentials doesn't change the databag.
