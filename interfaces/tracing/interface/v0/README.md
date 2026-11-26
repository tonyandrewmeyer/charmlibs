# tracing

## Direction

Tracing is done in a push-based fashion.
The receiving endpoint of the tracing backend, also referred to as an ingester, can support a number of different protocols, such as [otlp-grpc](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/otlp.md#otlpgrpc) and [otlp-http](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/otlp.md#otlphttp).
The tracing backend exposes, for each protocol it supports, an endpoint at which the server is ready to accept that protocol.
The directionality of the relation flows from the observer, the Tempo(-compliant) backend, to the observed: the application producing the traces.

## Behavior

Keywords are as in RFC 2119.

### Requirer

- MUST NOT write to either databag.
- MUST push traces to one or more of the provider's ingesters.
- MUST handle the provider supporting none of the protocols that the requirer can use.

### Provider

- MUST write the host at which the server is reachable to the application databag, from the leader unit.
- MUST run a server supporting one or more tracing protocols, such as [OTLP](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/otlp.md#opentelemetry-protocol-specification).
- MUST write, for each protocol it accepts, the port at which the server is listening along with the name of the protocol.
