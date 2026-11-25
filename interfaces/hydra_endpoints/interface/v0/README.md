# hydra_endpoints

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST serve the admin and public APIs at the URLs that it writes.
- MUST write `admin_endpoint` and `public_endpoint` to the application databag from the leader unit.
- MUST update the databag when either URL changes.

### Requirer

- MUST NOT write to either databag.
- MUST use the URLs to set up its integration with Hydra.
