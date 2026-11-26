# fiveg_n2

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `amf_ip_address`, `amf_hostname`, and `amf_port` to the application databag of every relation from the leader unit.
- SHOULD NOT write anything until the AMF is running and its IP address and hostname are known.
- MUST update the databag when the IP address or hostname changes.

### Requirer

- MUST NOT write to either databag.
- MUST use the IP address, the hostname, and the port from the provider (or a subset of them) to connect to the N2 interface.
- SHOULD treat the relation as not ready until the provider's application databag is valid.
