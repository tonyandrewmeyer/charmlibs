# profiling

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write its OTLP gRPC ingestion endpoint to the application databag from the leader unit.
- MUST accept profiles on that endpoint.
- If it has ingress, MUST advertise its ingress address, and otherwise MUST advertise its cluster-internal FQDN.
- MUST set `insecure` to `true` if the ingestion endpoint doesn't use TLS.
- MUST update the databag when the endpoint or its TLS configuration changes.

### Requirer

- MUST NOT write to either databag.
- SHOULD treat the relation as not ready until the provider's application databag is valid.
- MUST NOT use TLS for the endpoint if `insecure` is `true`, and MUST use TLS otherwise.
