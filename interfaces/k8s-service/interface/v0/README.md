# k8s-service

## Formats

There are two formats on this interface, and they don't work with each other:

- Most charms use the [serialized-data-interface](https://github.com/canonical/serialized-data-interface) (SDI) package. Each side writes the schema versions it supports to `_supported_versions`, and the provider writes `service-name` and `service-port` in a YAML-encoded `data` field. SDI is deprecated.
- Newer charms use the `k8s_service_info` library, where the provider writes `name` and `port` directly, and the requirer writes nothing.

A charm that only supports one format needs to be integrated with a charm that uses the same one.

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the Service details to the application databag from the leader unit, in one of the two formats.
- If it uses SDI, MUST write `_supported_versions`, and MUST NOT write `data` until the requirer's `_supported_versions` has a version in common with it.
- SHOULD set the Service name to a name that the requirer can resolve, such as `<name>.<namespace>`, for example `kfp-api.kubeflow`.
- MUST update the databag when the Service details change.

### Requirer

- If it uses SDI, MUST write `_supported_versions` to the application databag from the leader unit. Otherwise, MUST NOT write to either databag.
- SHOULD treat the relation as not ready until the provider's Service details are in the databag.
- SHOULD use the latest Service details when the provider changes them.
