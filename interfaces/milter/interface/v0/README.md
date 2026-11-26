# milter

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `port` to the unit databag of every unit that serves the milter, on every `milter` relation.
- MUST listen for milter connections on that port on the unit's `ingress-address`.

### Requirer

- MUST NOT write to either databag.
- MUST combine each provider unit's `port` with that unit's `ingress-address` from the same unit databag to connect.
- SHOULD ignore provider units that don't have an `ingress-address` yet.
- MAY fall back to port 8892 when a unit has an `ingress-address` but no `port`.
- MAY connect to only one of the provider's units per relation.
