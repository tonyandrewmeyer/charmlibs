# kratos_info

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write its endpoints, ConfigMap details, and feature flags to the application databag from the leader unit.
- SHOULD NOT write anything until it has an externally accessible URL, since `login_browser_endpoint` is based on it.
- MUST store the identity providers and identity schemas in the ConfigMaps that it names.
- MUST update the databag when its endpoints or configuration change.

### Requirer

- MUST NOT write to either databag.
- SHOULD treat the relation as not ready until the provider's application databag is populated.
- MUST use the data to set up its integration with Kratos.
