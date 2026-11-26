# cos_agent

## Behavior

Keywords are as in RFC 2119.

The relation MUST be a subordinate relation (`scope: container`), with the requirer as the subordinate charm, so both charms run on the same machine.
Each side communicates only through its unit databag.

### Provider

- Each unit MUST write its telemetry configuration to the `config` field of its unit databag, with every field present, even if empty.
- MUST include the Juju topology of the principal in the alert rules.
- MUST encode each dashboard as JSON, then compress it with LZMA, then base64-encode it.
- SHOULD use scrape targets on `localhost` for endpoints on its own machine.
- MAY list in `tracing_protocols` the tracing protocols it wants receivers for.
- MUST update the databag when its telemetry configuration changes.
- SHOULD treat a receiver whose `url` is `null`, or a protocol that isn't listed, as not available yet.

### Requirer

- Each unit MUST write `receivers` to its unit databag, with an entry for each protocol that any principal on its machine requested, even if it can't forward traces yet.
- MUST set a receiver's `url` to `null` until it can forward traces for that protocol.
- SHOULD scrape the provider's `metrics_scrape_jobs`, read logs from the provider's `log_slots`, and forward the provider's alert rules and dashboards to COS, with the provider's Juju topology.
- SHOULD remove the provider's alert rules and dashboards from COS when the relation is removed.
- SHOULD NOT fail when the provider's data is invalid.
