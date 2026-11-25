# fiveg_f1

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `f1_ip_address`, `f1_port`, `tac`, and `plmns` to the application databag from the leader unit.
- SHOULD NOT write anything until it has a TAC and at least one PLMN.
- MUST update the databag when any of these change.
- MUST use the requirer's `f1_port` to communicate with the DU over F1. It MAY use a default port until the requirer has written one.

### Requirer

- MUST write `f1_port` to the application databag from the leader unit.
- MUST use the IP address and port from the provider to establish communication over F1.
- MUST use the TAC and PLMNs from the provider to configure the DU.
- SHOULD treat the relation as not ready until the provider's application databag is valid.
