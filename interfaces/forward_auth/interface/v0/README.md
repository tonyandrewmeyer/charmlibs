# forward_auth

## Direction

The provider is part of an Identity and Access Proxy, and the requirer is an ingress. The applications in `app_names` are the ones that have asked the provider to protect them over the `auth_proxy` interface. The provider compares them with the requirer's `ingress_app_names` to check that each one has ingress, which is how its requests reach the provider.

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `decisions_address` and `app_names` to the application databag from the leader unit.
- MUST answer requests forwarded to `decisions_address` with whether the request is authenticated.
- MUST update `app_names` when an application asks to be protected or stops being protected.
- SHOULD report an error when an application in `app_names` isn't in the requirer's `ingress_app_names`.

### Requirer

- MUST write `ingress_app_names` to the application databag from the leader unit, and SHOULD update it when the applications it provides ingress to change.
- MUST delegate authentication of requests to the applications in `app_names` to `decisions_address`, for example with the Traefik ForwardAuth middleware.
- SHOULD copy the headers in `headers` from the provider's response to the forwarded request.
- SHOULD treat the relation as not ready until the provider's application databag has `decisions_address` and `app_names`.
- SHOULD stop delegating authentication when the relation is removed.
