# ingress

## Behavior

Keywords are as in RFC 2119.

Version 1 is deprecated: new charms SHOULD use version 2, which load-balances across all of the requirer's units instead of routing all traffic to its leader.

### Provider

- MUST write the ingress URL to the application databag from the leader unit.
- MUST route traffic for the URL to `host` and `port` (that is, to the requirer's leader unit).
- MUST update the URL when it changes, for example when the ingress's external hostname changes.
- MAY choose the form of the URL. The conventional form, used by `traefik-k8s` in its default path routing mode, is `<scheme>://<ingress-address>/<model>-<name>`.
- MAY ignore `strip-prefix` and `redirect-https` if it doesn't support them.

### Requirer

- MUST write the application data from the leader unit.
- SHOULD rewrite its data when leadership changes and when the charm is upgraded.
- MUST declare the endpoint with `limit: 1`, because the ingress URL is per application.
- MUST NOT use a URL until the provider has written one, and SHOULD stop using it when the relation is removed.
