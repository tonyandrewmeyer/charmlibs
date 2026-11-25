# fiveg_gnb_identity

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `gnb_name` and `tac` to the application databag of every relation from the leader unit.
- MUST update the databag when the TAC changes.

### Requirer

- MUST NOT write to either databag.
- MUST use the name and TAC from the provider to identify the gNodeB.
