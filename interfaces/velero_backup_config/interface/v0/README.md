# velero_backup_config

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `app`, `relation_name`, `model`, and `spec` to the application databag from the leader unit.
- MUST set `app` to its application name, `relation_name` to the name of its endpoint for this relation, and `model` to the name of its model, because the requirer identifies the backup target by these.
- MUST write one backup specification per relation. To have different sets of data backed up separately, it MAY use several endpoints with this interface, one for each set.
- SHOULD write the backup specification as soon as the relation is created, and SHOULD update it when what it needs backed up changes.
- If it sets `ttl`, MUST use a duration that Velero accepts, in hours, minutes, and seconds (such as `72h`). Days (such as `30d`) aren't accepted.

### Requirer

- MUST NOT write to either databag.
- MUST support relations from several providers at once, and MUST identify each backup target by the provider's `app`, `relation_name`, and `model`.
- When a backup of a target is requested, MUST create a Velero backup from that target's backup specification.
- If a backup specification has `schedule` set, SHOULD create or update a Velero schedule from it. SHOULD delete that schedule when `schedule` is removed or the relation is removed.
