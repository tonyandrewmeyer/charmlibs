# tls-certificates

## Behavior

Keywords are as in RFC 2119.

### Requirer

- MUST generate a private key, or use an existing one, and MUST NOT write it to the relation data.
- MUST write a certificate signing request (CSR) for each certificate that it needs, and MUST say for each one whether it is for a certificate authority (CA).
- MUST write the CSRs for certificates that a unit uses to that unit's databag, and the CSRs for certificates that the whole application uses to the application databag, from the leader unit.
- MUST stop using a certificate that the provider has marked as revoked.
- SHOULD request a new certificate before the current one expires.
- MUST NOT treat a capability that the provider leaves out as having a default value, and MUST NOT assume that a provider has any capabilities if it doesn't advertise them.

### Provider

- MUST write to the application databag from the leader unit.
- For each CSR that it processes successfully, MUST provide the certificate, the CA certificate, and the CA chain in `certificates`.
- For each CSR that it can't process, SHOULD provide an error in `request_errors` that says why.
- MUST NOT have a CSR in both `certificates` and `request_errors`.
- MUST replace or remove the existing certificates in the relation data when it issues new ones, and SHOULD remove certificates for CSRs that the requirer no longer has.
- SHOULD mark its certificates as revoked when they are no longer valid, for example when its CA changes.
- MAY advertise what it can issue in `capabilities`, on a best-effort basis.

## Error codes

Errors have both a numeric `code` and a machine-readable `name`.

| Code    | Name                   | Description                                                    |
| ------- | ---------------------- | -------------------------------------------------------------- |
| **1XX** | **csr_error**          | **Errors related to the certificate request itself**           |
| 101     | `ip_not_allowed`       | IP addresses are not allowed in the CSR by the provider        |
| 102     | `domain_not_allowed`   | The domain requested by the CSR is not allowed by the provider |
| 103     | `wildcard_not_allowed` | Wildcard certificates are not allowed by the provider          |
| **2XX** | **server_error**       | **Server-related errors**                                      |
| 201     | `server_not_available` | The provider backend is not reachable (e.g., Vault is sealed)  |
| **9XX** | **other**              | **Other errors not covered by the above categories**           |

## Backward compatibility

`request_errors` and `capabilities` are optional and additive. Requirers that don't understand them continue to work, without the error information or capabilities. Providers that don't support `request_errors` leave a CSR that they can't process out of both lists.
