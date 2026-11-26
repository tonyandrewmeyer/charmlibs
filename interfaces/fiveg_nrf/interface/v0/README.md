# fiveg_nrf

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write `url` to the application databag of every relation from the leader unit.
- SHOULD NOT write anything until the NRF is running.
- MUST update the databag when the URL changes.

### Requirer

- MUST NOT write to either databag.
- MUST use the provider's URL to register itself, to learn about registered network functions, or both.
