# litmus_auth

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write its gRPC server's host and port to the application databag from the leader unit.
- MUST set `insecure` to `true` if its gRPC server can't accept TLS connections.
- MUST set `version` to `0`. The library treats a databag without `version` as not ready.
- MUST connect to the requirer's gRPC server with TLS unless the requirer's `insecure` is `true`.

### Requirer

- MUST write its gRPC server's host and port to the application databag from the leader unit.
- MUST set `insecure` to `true` if its gRPC server can't accept TLS connections.
- MUST set `version` to `0`. The library treats a databag without `version` as not ready.
- MUST connect to the provider's gRPC server with TLS unless the provider's `insecure` is `true`.
