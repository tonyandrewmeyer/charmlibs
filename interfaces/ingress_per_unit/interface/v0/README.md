# ingress_per_unit

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST provide ingress for each requirer unit that has written valid unit data, using the `host`, `port`, `mode` and `scheme` that the unit gives.
- MUST treat a missing `mode` or `scheme` as `http`.
- MUST write `ingress` from the leader unit only, with an entry keyed by the `name` of each unit it provides ingress for.
- In `http` mode, MUST publish the full URL at which the unit is reachable; in `tcp` mode, MUST publish the `host:port` at which the unit is reachable.
- SHOULD strip the path prefix from requests before forwarding them to a unit that sets `strip-prefix` to `true`.
- SHOULD stop providing ingress for the relation if its units give different `model` values.
- SHOULD remove the entries for units that leave the relation or stop sending valid data.
- MUST remove or replace entries whose URLs are no longer valid, for example when the provider's external address changes.
- MUST update `ingress` when a unit's data changes.

### Requirer

- Each unit that needs ingress MUST write its own data to its own unit databag.
- All units MUST give the same `model`.
- SHOULD update its unit data when the host, port or scheme it serves on changes.
- MUST treat its ingress as not ready until its unit name appears in `ingress`, and as revoked when its unit name disappears.
- SHOULD treat a change to its unit's entry in `ingress` as a new URL.
