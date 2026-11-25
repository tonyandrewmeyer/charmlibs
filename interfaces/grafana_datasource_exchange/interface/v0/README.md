# grafana_datasource_exchange

## Behavior

Keywords are as in RFC 2119.

The interface is symmetrical: the provider and the requirer write the same data, and follow the same rules.
A charm MAY implement a provider endpoint, a requirer endpoint, or both, so that it can be integrated with any other charm that implements the interface.

### Provider

- MUST expose one or more datasources that Grafana can query, and register them with Grafana (for example, over the `grafana_datasource` interface) to get a UID for each one.
- MUST write `datasources` to the application databag from the leader unit, with an entry for each datasource, typically one for each unit.
- MUST only include a datasource once Grafana has assigned its UID, so that every entry has a `type`, `uid`, and `grafana_uid`.
- MUST sort `datasources` by `uid`, so that the databag doesn't keep changing and cause endless cascades of `relation-changed` events.
- MUST eventually write the datasources. Because the UIDs come from another relation, it can't rely on a particular event, or on which relation is created first.

### Requirer

- MUST follow the same rules as the provider.
