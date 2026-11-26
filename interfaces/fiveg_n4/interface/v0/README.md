# fiveg_n4

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `upf_hostname` and `upf_port` to the application databag of every relation from the leader unit.
- MUST update the databag when the hostname changes.

### Requirer

- MUST NOT write to either databag.
- MUST use the hostname and the port from the provider to establish communication over the UPF's N4 interface.
