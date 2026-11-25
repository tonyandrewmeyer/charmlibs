# etcd_client

## Behavior

Keywords are as in RFC 2119.

Both charms MUST support Juju secrets: sensitive fields are sent in Juju secrets rather than in the databag, with related fields grouped together in one secret. The library raises an error when the relation is initialised if either side doesn't support them.

### Provider

- MUST write to the application databag from the leader unit.
- MUST NOT create a user until the requirer has provided a valid client certificate.
- MUST create a user with the common name from the client certificate (`mtls-cert`) that the requirer provides.
- MUST create a role with read and write permissions on the keys under the requirer's `prefix`, and grant the role to that user.
- MUST delete the user and role when the relation is removed.
- MUST add the requirer's client certificate to the provider's truststore, MUST update the truststore when the certificate changes, and MUST remove the certificate from the truststore when the relation is removed.
- MUST put the name of the user (`username`) and a comma-separated list of the cluster's client URLs (`uris`) in a Juju secret, and write the secret's ID to `secret-user`.
- MUST write `endpoints`, a comma-separated list of all the cluster endpoints.
- MUST write `version`, the installed version of etcd.
- MUST put the CA certificate of the server in `tls-ca` in a Juju secret, and write the secret's ID to `secret-tls`. MAY also put `True` in `tls` in that secret, as older providers do. (etcd only supports clients when it has TLS enabled.)

### Requirer

- MUST write `requested-secrets`, a JSON array of the names of the fields that the provider should put in Juju secrets rather than in the databag. The names MUST be valid Juju secret keys (alphanumeric characters and dashes). It normally includes `username`, `uris`, `tls`, and `tls-ca`.
- MUST write `provided-secrets`, a JSON array of the names of the fields that the requirer puts in Juju secrets, in the same format. It normally includes `mtls-cert`.
- MUST write `prefix`, the range of keys that it wants to access.
- MUST put its client certificate in `mtls-cert` in a Juju secret, and write the secret's ID to `secret-mtls`. In a cross-model relation, where it can't use a secret, MUST instead write the certificate to `mtls-cert`, encrypted with the key in the provider's `encryption-secret`.
