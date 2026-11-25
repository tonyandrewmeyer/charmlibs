# dns_record

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the statuses to the application databag from the leader unit.
- MUST ignore requested entries that don't have a `uuid`.
- MUST report the status of each request under the `uuid` that the requirer gave it.
- MUST update the statuses when the requested entries, or the outcome of processing them, change.
- MUST stop serving a record when the requirer removes its entry from `dns_entries`.
- MAY reject a request that the requirer isn't allowed to make, with the `permission_denied` status.
- MAY reject requests that are for the same domain, host label, record class and record type as another request, with the `conflict` status.
- MAY allocate a domain for the requirer and publish it in `ddns-domain`. If it does, it MUST point the domain at the addresses in the requirer's `ddns-addresses` if they are set, and at the `ingress-address` of the requirer's units otherwise, and it MUST remove `ddns-domain` when it stops allocating domains.
- If it allocates domains, SHOULD reject requests for `A`, `AAAA` and `CNAME` records in the allocated domains, with the `permission_denied` status.

### Requirer

- MUST write the requested entries to the application databag from the leader unit.
- MUST give each entry a `uuid` that is unique within the relation, and SHOULD keep it the same for as long as the entry is unchanged.
- MUST set `ttl` and `record_type` on each entry, as providers ignore entries without them.
- MUST publish the complete list of entries it wants each time it updates `dns_entries`; leaving an entry out withdraws the request.
- SHOULD ignore statuses for UUIDs that it didn't request.
- MAY set `ddns-addresses` when the `ingress-address` of its units isn't publicly reachable, for example because it's behind a NAT.
