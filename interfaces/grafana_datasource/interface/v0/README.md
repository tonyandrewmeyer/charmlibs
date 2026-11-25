# grafana_datasource

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST serve an API that Grafana can query as a datasource of the `type` it sets. The types are in Grafana's [datasources documentation](https://grafana.com/docs/grafana/latest/datasources/).
- MUST write `grafana_source_data` to the application databag from the leader unit.
- MUST write the URL of each unit's server to `grafana_source_host` in that unit's databag, or the URL of a single address for the whole application, such as a load balancer or an ingress, to `grafana_source_app_host` in the application databag from the leader unit, or both.
- MUST update the URLs when they change.
- MAY share the datasource UIDs that the requirer writes with other charms, for correlation.

### Requirer

- MUST add a datasource to Grafana for each provider unit that has set `grafana_source_host`, and one for the application if the provider has set `grafana_source_app_host`, with `extra_fields` as the datasource's `jsonData` and `secure_extra_fields` as its `secureJsonData`.
- MUST write `grafana_uid`, a unique ID for the Grafana application, to the application databag from the leader unit.
- MUST write to `datasource_uids` the UID of each provider unit's datasource, and, if there is a datasource for the application, MUST write its UID to `app_datasource_uid`.
- SHOULD keep each datasource's UID the same for as long as the datasource exists.
- SHOULD write Grafana's base URL, which may be an ingress URL, to `grafana_base_url`.
- MUST remove a datasource when the provider unit or relation that it is for is removed.
