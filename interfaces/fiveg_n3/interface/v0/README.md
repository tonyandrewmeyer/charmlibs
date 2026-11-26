# fiveg_n3

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `upf_ip_address` to the application databag of every relation from the leader unit.
- SHOULD NOT write anything until the IP address of its N3 (access) interface is known.
- MUST update the databag when the IP address changes.

### Requirer

- MUST NOT write to either databag.
- MUST use the UPF's IP address to establish communication over the N3 interface.
