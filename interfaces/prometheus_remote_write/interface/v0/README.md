# prometheus_remote_write

## Direction

Metrics flow from the requirer to the provider: the requirer sends its metrics to the remote write endpoints that the provider's units publish. Rules flow the same way: the requirer publishes alert and recording rules, and the provider evaluates them against the metrics it receives.

## Behavior

Keywords are as in RFC 2119.

### Provider

- Each unit that can receive metrics MUST write the URL of its remote write endpoint to its unit databag, and MUST accept metrics sent there with the Prometheus remote write protocol.
- MUST keep the Juju topology labels that the requirer adds to its metrics.
- MUST load the requirer's alert and recording rules, and evaluate them.
- MUST add each rule's Juju topology labels to its expression as label matchers.
- MUST NOT add a `juju_unit` label matcher to an expression, but MUST keep one that is already there.
- MUST set `alert_rules_encodings` if it can read any encoding other than `json`, and MUST be able to read rules in every encoding it lists.
- MUST be able to read `json` rules, whether or not it lists `json`, so that rules from a requirer of any version are never lost.
- MUST write the same `alert_rules_encodings` value each time, so that publishing it again doesn't change the databag.
- MUST publish `alert_rules_encodings` again when leadership changes and when the charm is upgraded, so that relations made before the provider could read other encodings learn about it.
- MUST report rules that it can't use, because they failed validation or couldn't be decoded, in the `errors` field of `event`, rather than dropping them silently. MUST remove the error once the rules can be used.
- MAY show the requirer's rule errors in its own status.

### Requirer

- MUST send all its metrics to every endpoint that the provider's units publish. If more than one unit publishes the same URL (for example, behind an ingress), SHOULD send the metrics to it only once.
- MUST add the Juju topology labels it wants to every metric it sends.
- MUST publish its alert and recording rules in `alert_rules`, with an empty object if it has none.
- MUST add its Juju topology to every rule as labels, and MUST put any other label matchers it wants as labels on the rule, so that the provider can add them to the expression.
- MUST encode its rules as `json`, unless the provider lists another encoding that the requirer supports in `alert_rules_encodings`. MAY use any listed encoding that it supports, whatever the order.
- MUST ignore encodings it doesn't recognise, and MUST use `json` if it recognises none of them.
- MUST choose the encoding again whenever the provider's application databag changes, since the provider's `alert_rules_encodings` might only arrive after the relation is joined.
- MUST write its rules deterministically (for example, with sorted keys), so that unchanged rules give an unchanged value and don't cause a spurious `relation-changed` event on the provider.
- MAY show the errors that the provider reports in `event` to the user.
