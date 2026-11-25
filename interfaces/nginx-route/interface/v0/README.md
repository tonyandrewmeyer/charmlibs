# nginx-route

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST create Nginx ingress resources in the Kubernetes cluster, with host-based routing, when the requirer's configuration is valid.
- If the requirer's configuration is not valid (for example, `service-hostname`, `service-name`, or `service-port` is missing, or a hostname is invalid), MUST ignore the request and report the error in its status.
- SHOULD update the ingress resources when the requirer's application databag changes.
- SHOULD remove the ingress resources when the relation is removed.
- MUST NOT write to either databag.
- MAY give its own configuration precedence over the requirer's values.

### Requirer

- MUST write a valid ingress configuration to the application databag from the leader unit.
- SHOULD set `service-namespace` to the namespace the service runs in, since the provider otherwise uses the namespace of its own model.
- SHOULD remove keys for options it no longer sets, so that the databag holds exactly its current configuration.
- MUST NOT write to the unit databags.

## Precedence in the Nginx Ingress Integrator charm

The databag keys match the options of the Nginx Ingress Integrator charm's configuration. When an option is set in that charm's configuration, it takes precedence over the value in the relation, except for `service-name`, `service-port`, and `path-routes`, where the relation value takes precedence. Options whose configuration default is not empty, such as `max-body-size` and the `proxy-*` timeouts, therefore only take effect from the relation when the charm's configuration sets them to 0.
