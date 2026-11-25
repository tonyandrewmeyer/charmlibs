# sdcore_management

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `management_url` to the application databag of every relation from the leader unit.
- SHOULD NOT write anything until the address of the service is known.
- MUST update the databag when the address changes.

### Requirer

- MUST NOT write to either databag.
- MUST use the address from the provider to connect to the configuration service.
