# tracing

## Direction

Tracing is done in a push-based fashion.
The receiving endpoint of the tracing backend, also referred to as a _receiver_, can support a number of different protocols, such as [otlp-grpc](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/otlp.md#otlpgrpc) and [otlp-http](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/otlp.md#otlphttp).
The requirer initializes the interface by publishing a list of receiver protocols it intends to use to send traces to the provider.
The provider replies with, for each requested protocol that it supports, an endpoint at which the server is ready to accept that protocol. If the provider does not support a requested protocol, it omits that from the response. This means that if no requested protocol is supported, the reply has no receivers.

The directionality of the relation flows from the observer, the Tempo(-compliant) backend, to the observed: the application producing the traces.

## Behavior

Keywords are as in RFC 2119.

### Requirer

- MUST write a list of one or more protocols that it wants to use to send traces to the application databag, from the leader unit.
- MUST wait for the provider's list of receivers before sending traces.
- MUST only push traces to receivers in the provider's list, using the protocol of that receiver.
- MUST handle the provider supporting none of the requested protocols.

### Provider

- MUST write the list of receivers to the application databag from the leader unit.
- MUST write the list of receivers once it has read a request, even if it is empty, as an acknowledgement of the request.
- MUST enable a receiver for each requested protocol that it supports, and MUST NOT list a receiver for a protocol that it doesn't support.
- MUST accept traces on every receiver that it lists.
- MAY list receivers that this requirer didn't request, such as ones that other requirers requested.
- MUST update the list when the requested protocols or the receivers' URLs change.
