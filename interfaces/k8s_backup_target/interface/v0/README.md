# k8s_backup_target

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `backup_targets` to the application databag from the leader unit.
- In each entry in `backup_targets`, MUST set `app` to its application name, `relation_name` to the name of its endpoint for this relation, and `model` to the name of its model, because the requirer identifies the backup target by these.
- SHOULD write `backup_targets` as soon as the relation is created, and SHOULD update it when what it needs backed up changes.
- If it sets `ttl`, MUST use a duration in hours, minutes, and seconds (such as `72h`). Days (such as `30d`) aren't accepted.

### Requirer

- MUST NOT write to either databag.
- MUST identify each backup target by its `app`, `relation_name`, and `model`.
- SHOULD ignore a provider databag that it can't parse, rather than failing.
- If it forwards backup specifications to a backup operator (as an integrator charm does), SHOULD forward each backup target it receives, and SHOULD update what it has forwarded when the relation data changes or the relation is removed.

## Backup specification

The backup specification in `spec` is based on [Velero's resource filtering](https://velero.io/docs/main/resource-filtering/), but is meant to be general enough for other backup operators to use.
