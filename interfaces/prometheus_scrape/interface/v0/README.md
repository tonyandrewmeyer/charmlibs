# prometheus_scrape

## Direction

The requirer pulls metrics from the provider: the provider publishes scrape jobs and the address of each of its units, and the requirer scrapes them. The provider also publishes alert and recording rules, which the requirer evaluates against the metrics it scrapes. The requirer reports jobs and rules that it can't use back to the provider.

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST publish scrape jobs for its metrics endpoints in `scrape_jobs`, and its Juju topology in `scrape_metadata`. A provider that only forwards rules MAY leave out both.
- Each unit that can be scraped MUST write its address and name to its unit databag, and MUST update the address when it changes (for example, when the unit's pod is rescheduled).
- If the provider is behind an ingress or a proxy, each unit MUST write the address and path prefix of the ingress or proxy. Otherwise, each unit SHOULD write its fully qualified domain name.
- MUST publish its alert and recording rules in `alert_rules`.
- MUST add its Juju topology to every rule as labels, and MUST put any other label matchers it wants as labels on the rule, so that the requirer can add them to the expression.
- MAY leave the Juju topology label matchers out of the rule expressions, since the requirer adds them.
- MUST NOT replace the Juju topology labels that the requirer adds to its metrics.
- MAY show the errors that the requirer reports in `event` in its own status.

### Requirer

- MUST run the provider's scrape jobs, replacing the `*` host in each target with the address of each of the provider's units, and adding the unit's path prefix to the metrics path.
- MUST label the scraped metrics with the provider's Juju topology from `scrape_metadata`, and with `juju_unit` for targets that are one of the provider's units.
- SHOULD give each job a name that is unique across all providers, for example by prefixing it with the provider's Juju topology.
- MUST load the provider's alert and recording rules, and evaluate them.
- MUST add each rule's Juju topology labels to its expression as label matchers.
- MUST NOT add a `juju_unit` label matcher to an expression, but MUST keep one that is already there.
- SHOULD report scrape jobs that it can't use in the `scrape_job_errors` field of `event`, and rules that it can't use in the `errors` field, and MUST remove each error once the jobs or rules can be used.
