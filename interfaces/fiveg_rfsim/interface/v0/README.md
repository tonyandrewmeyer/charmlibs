# fiveg_rfsim

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write to the application databag from the leader unit, with `version` set to the version of the interface that it uses.
- MUST NOT write anything unless the requirer's `version` is the same as its own.
- MUST write the radio settings (`band`, `dl_freq`, `carrier_bandwidth`, `numerology`, and `start_subcarrier`), because requirers treat the data as invalid without them.
- MUST update the databag when any of these change.

### Requirer

- MUST write `version` to the application databag from the leader unit, set to the version of the interface that it uses.
- MUST NOT use the provider's data if the provider's `version` is not the same as its own.
- MUST use the RF simulator's address, the network slice (SST and SD), and the radio settings from the provider to connect.
