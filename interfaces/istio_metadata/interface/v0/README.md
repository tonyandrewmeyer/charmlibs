# istio_metadata

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the metadata to the application databag from the leader unit.
- MUST set `root_namespace` to the namespace that the Istio control plane is installed in.
- SHOULD publish the metadata when the relation is joined and when a new leader is elected.

### Requirer

- MUST NOT write to either databag.
- SHOULD set `limit: 1` on its endpoint, since the metadata describes a single Istio installation.
- SHOULD treat the relation as not ready until the provider's application databag is populated.
