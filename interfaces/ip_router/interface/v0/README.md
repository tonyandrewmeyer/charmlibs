# ip_router

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST have an interface available at the gateway address of every network that a requirer requests.
- MUST implement the routes that the requirers request.
- MUST write the routing table, with the networks from every requirer, to `networks` in the application databag of every relation from the leader unit.
- MUST update the routing table when a requirer changes its request, or when a relation is removed.

### Requirer

- MUST write the networks that it requests to `networks` in the application databag from the leader unit.
- MUST include every network that it needs in each request, because a request replaces the previous one.
- MUST use network names that are unique among all the requirers of the same provider.
- MUST NOT request a network that overlaps a network that another requirer has requested.
- MUST request networks whose gateway, and the gateway of each of their routes, is in the network.
