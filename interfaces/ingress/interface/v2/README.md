# ingress

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the ingress URL to the application databag from the leader unit.
- SHOULD NOT provide ingress until the requirer's application databag and every requirer unit's databag hold valid data.
- MUST route traffic for the URL to `port` on each of the requirer's units, addressing each unit by its `host` or `ip`, and SHOULD load-balance across those units.
- MUST update the URL when it changes, for example when the ingress's external hostname changes.
- SHOULD leave the application databag empty rather than write a URL that isn't valid.
- MAY choose the form of the URL. The conventional form, used by `traefik-k8s` in its default path routing mode and by `istio-ingress-k8s`, is `<scheme>://<ingress-address>/<model>-<name>`.
- MAY ignore any of `strip-prefix`, `redirect-https`, `scheme`, and `healthcheck_params` that it doesn't support. These are additions on top of the basic request, and not every provider honours all of them.

### Requirer

- MUST write the application data from the leader unit.
- MUST have every unit write its own unit databag, so that the provider can reach each unit.
- SHOULD rewrite its data when leadership changes and when the charm is upgraded.
- MUST declare the endpoint with `limit: 1`, because the ingress URL is per application.
- MUST NOT use a URL until the provider has written one, and SHOULD stop using it when the relation is removed.
