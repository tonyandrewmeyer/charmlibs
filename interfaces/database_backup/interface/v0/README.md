# database_backup

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST detect new jobs, and run a backup or a restore depending on `job-type`.
- SHOULD run backups concurrently where it can (for example, an incremental or point-in-time recovery backup can sometimes run alongside a full backup), but MUST NOT run more than one restore at a time.
- MUST use locking to avoid running incompatible jobs, such as a backup and a restore, at the same time.
- MUST report the status of the current or most recently completed job in the unit databag of the unit that ran it.
- For a backup, MUST upload the backup and log artefacts to the job's storage.
- For a restore, MUST retrieve the backup artefacts from the job's storage.

### Requirer

- MUST give the storage configuration for each job.
- MUST relay the results of completed jobs back to the Juju admin.
- MUST keep the history of completed and running jobs, and MUST provide a way to clear the history of completed jobs.
