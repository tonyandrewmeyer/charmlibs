# fiveg_core_gnb

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `tac` and `plmns` to the application databag from the leader unit.
- MUST write, in each relation, the configuration of the CU or gNodeB that the requirer names in `gnb-name`.
- SHOULD NOT write anything in a relation until it has a configuration for the CU or gNodeB that the requirer names.
- SHOULD add the CU or gNodeB to its configuration under the requirer's `gnb-name`, and SHOULD remove it when the relation is removed.
- MUST update the databag when the configuration of the CU or gNodeB changes.

### Requirer

- MUST write `gnb-name` to the application databag from the leader unit.
- MUST use a `gnb-name` that is unique among the CUs and gNodeBs that are related to the same provider.
- MUST use the TAC and PLMNs from the provider to configure the CU or gNodeB.
- SHOULD treat the relation as not ready until the provider's application databag has a valid `tac` and `plmns`.
