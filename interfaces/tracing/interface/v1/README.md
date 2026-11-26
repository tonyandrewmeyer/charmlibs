# tracing

## Direction

Tracing is done in a push-based fashion.
The receiving endpoint of the tracing backend, also referred to as a _receiver_, can support a number of different protocols, such as [otlp-grpc](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/otlp.md#otlpgrpc) and [otlp-http](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/otlp.md#otlphttp).
The requirer initializes the interface by publishing a list of receiver protocols it intends to use to send traces to the provider.
The provider replies with, for each requested protocol, an endpoint at which the server is ready to accept that protocol. If the provider does not support a requested protocol, it omits that from the response. This means that if no requested protocol is supported, the reply may contain no protocol-specific receiver ports (it still contains the host).

The directionality of the relation flows from the observer, the Tempo(-compliant) backend, to the observed: the application producing the traces.

## Behavior

Keywords are as in RFC 2119.

### Requirer

- MUST write a list of one or more protocols that it wants to use to send traces to the application databag, from the leader unit.
- MUST wait for the provider's list of receivers before sending traces.
- MUST push traces to one or more of the provider's receivers, using the corresponding protocol.
- MUST handle the provider supporting none of the requested protocols.

### Provider

- MUST write the host at which the server is reachable to the application databag, from the leader unit. This happens in any case, and doubles as an acknowledgement of the request.
- SHOULD enable a receiver for each requested protocol that it supports.
- MUST run a server accepting traces on all the protocols that are both supported and requested.
- MUST write, for each protocol it accepts, the port at which the server is listening along with the name of the protocol.
