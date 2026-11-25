# mimir_cluster

## Behavior

Keywords are as in RFC 2119.

The interface is only intended to be used between the `mimir-coordinator-k8s` and `mimir-worker-k8s` charms.

### Provider

- MUST write to the application databag from the leader unit.
- SHOULD NOT write to a relation until every worker unit has written its address and topology and the worker application has written its roles.
- MUST write a working Mimir configuration to `worker_config`, for the workers to run with.
- MUST include the addresses of all worker units, whatever their roles, in the gossip ring (memberlist) configuration.
- MAY set `worker_ports` to the ports that the worker needs.
- If it sets `privkey_secret_id`, MUST grant that secret to the relation.
- MUST update the databag when the configuration changes.

### Requirer

- The leader unit MUST write the application's roles to the application databag as soon as possible.
- Each unit MUST write its address (FQDN) and Juju topology to its unit databag as soon as possible.
- MUST run the workload with `worker_config`.
- If `worker_ports` is set, SHOULD open those ports.
- SHOULD only configure TLS when `ca_cert`, `server_cert`, and `privkey_secret_id` are all set, and MUST read the private key from the `private-key` key of that secret.
- SHOULD push its logs, metrics, and traces to the endpoints in `loki_endpoints`, `remote_write_endpoints`, `charm_tracing_receivers`, and `workload_tracing_receivers`, when they are set.
- SHOULD treat the cluster as removed if the provider's application databag becomes empty or invalid after the requirer has written its data.
