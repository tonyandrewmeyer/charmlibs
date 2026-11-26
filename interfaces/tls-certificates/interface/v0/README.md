# tls-certificates

## Behavior

Keywords are as in RFC 2119.

### Requirer

- MUST write a list of certificate requests, for server certificates, client certificates, or both, to its unit databag.
- SHOULD write its unit name to its unit databag.

### Provider

- MUST write its CA certificate and CA chain to its unit databag.
- MUST write a certificate and private key for each certificate request to its unit databag, as a JSON object with `cert` and `key`, under a key that is the request's common name.
- MUST overwrite the existing certificates, or remove them, when it issues new ones.
