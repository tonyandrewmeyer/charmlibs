"""This file defines the schemas for the provider and requirer sides of the prometheus_remote_write interface."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, Json, StringConstraints

CompressedAlertRules = Annotated[str, StringConstraints(pattern=r'^/Td6WFoA')]
"""Alert rules, LZMA-compressed and base64-encoded.

`/Td6WFoA` is the base64 encoding of the xz magic bytes, which every compressed payload starts with.
"""


class RemoteWrite(BaseModel):
    """A remote write endpoint."""

    model_config = ConfigDict(extra='forbid')

    url: str = Field(
        description='The URL the requirer should send metrics to with remote write.',
        examples=['http://192.168.1.2:9090/api/v1/write'],
    )


class Event(BaseModel):
    """Feedback to the requirer about the alert rules it published."""

    model_config = ConfigDict(extra='allow')

    errors: str | None = Field(
        default=None,
        description='Why the requirer\'s alert rules could not be used, for example because they failed validation or could not be decoded. Absent while the rules are usable.',
        examples=[
            'error validating rule: could not parse expression',
            'Could not decode the published alert rules: Alert rules must be a JSON object, not list',
        ],
    )


class AlertRule(BaseModel):
    """An alerting or recording rule, as in a Prometheus rule file.

    Rules can have any other field that Prometheus allows, such as `keep_firing_for`.
    """

    model_config = ConfigDict(extra='allow')

    alert: str | None = Field(
        default=None,
        description='The name of the alert. Set for alerting rules.',
        examples=['ConsumerCharmUnavailable'],
    )
    record: str | None = Field(
        default=None,
        description='The name of the time series to record the result in. Set for recording rules.',
        examples=['job:http_requests:rate5m'],
    )
    expr: str = Field(
        description='The PromQL expression to evaluate.',
        examples=[
            'up{juju_model="some-model",juju_model_uuid="00000000-0000-0000-0000-000000000000",juju_application="consumer-charm"} < 1'
        ],
    )
    for_: str | None = Field(
        default=None,
        alias='for',
        description='How long the expression must be true before the alert fires.',
        examples=['0m', '5m'],
    )
    labels: dict[str, str] = Field(
        description='Labels to add to the alert or the recorded series, including the Juju topology labels.',
        examples=[
            {
                'severity': 'critical',
                'juju_model': 'some-model',
                'juju_model_uuid': '00000000-0000-0000-0000-000000000000',
                'juju_application': 'consumer-charm',
            }
        ],
    )
    annotations: dict[str, str] | None = Field(
        default=None,
        description='Annotations to add to the alert. The values are templates, expanded when the alert fires.',
        examples=[
            {
                'summary': 'Consumer Charm {{ $labels.juju_model }}/{{ $labels.juju_unit }} unavailable'
            }
        ],
    )


class AlertRuleGroup(BaseModel):
    """A group of rules, as in a Prometheus rule file.

    Groups can have any other field that Prometheus allows, such as `interval`.
    """

    model_config = ConfigDict(extra='allow')

    name: str = Field(
        description='The name of the group.',
        examples=['some-model_00000000-0000-0000-0000-000000000000_consumer-charm_alerts'],
    )
    rules: list[AlertRule] = Field(
        description='The rules in the group.',
        examples=[
            [
                {
                    'alert': 'ConsumerCharmUnavailable',
                    'expr': 'up < 1',
                    'for': '0m',
                    'labels': {'severity': 'critical'},
                }
            ]
        ],
    )


class AlertRules(BaseModel):
    """Rules in the format of a Prometheus rule file."""

    model_config = ConfigDict(extra='forbid')

    groups: list[AlertRuleGroup] = Field(
        default_factory=list,
        description='The rule groups. Absent when the requirer has no rules.',
        examples=[
            [
                {
                    'name': 'some-model_00000000-0000-0000-0000-000000000000_consumer-charm_alerts',
                    'rules': [
                        {
                            'alert': 'ConsumerCharmUnavailable',
                            'expr': 'up < 1',
                            'for': '0m',
                            'labels': {'severity': 'critical'},
                        }
                    ],
                }
            ]
        ],
    )


_JSON_RULES = (
    '{"groups": [{"name": "some-model_00000000-0000-0000-0000-000000000000_consumer-charm_alerts", '
    '"rules": [{"alert": "ConsumerCharmUnavailable", "annotations": {"description": "The Consumer Charm '
    '{{ $labels.juju_model }} {{ $labels.juju_unit }} is unavailable LABELS = {{ $labels }}\\n", '
    '"summary": "Consumer Charm {{ $labels.juju_model}}/{{ $labels.juju_unit }} unavailable"}, '
    '"expr": "up{juju_model=\\"some-model\\",juju_model_uuid=\\"00000000-0000-0000-0000-000000000000\\", '
    'juju_application=\\"consumer-charm\\"} < 1", "for": "0m", "labels": {"juju_application": '
    '"consumer-charm", "juju_model": "some-model", "juju_model_uuid": "00000000-0000-0000-0000-000000000000", '
    '"severity": "critical"}}]}]}'
)
_LZMA_RULES = (
    '/Td6WFoAAATm1rRGAgAhARYAAAB0L+Wj4AKxASldAD2IiOdj/FO+er8ludNiIOGP157QqGtpLb+UcZYVMe8lCM1Ta6HUpl865IX7aJo4'
    'VJ+Avb3YcvBbwcBoXxSLw798TKy6thm5WVNHjMVwSB+htM6lCDuzSsxHLK8WB7V5it9M6QFrbfqAb9SW1qDLQbkUHaERDlnrEJ4Z+Q/f'
    'Ce51dVSmtFQ4MAfYQtE44YLH3DDrrGGEnrL1x+HCpOkmScSu61MUPFj5glrgvVeU3dEWpD9GitXYokMbsmGPHWP6FWRO3cE/FOjOyVae'
    'NKas8/pnvOrQw0QY6VBIlGIgUv4YPgU9zA7ZFZ7A6QFpnqTtChBmZCvKzeWfMIimODLKg5Cw3e90Ntxb9nELE+Ji2nnHD4Zszp0Rslfb'
    'nSffnxxenat+yDaS1SgUKgAAAADfB7I9BeI/0gABxQKyBQAAQEwASbHEZ/sCAAAAAARZWg=='
)


class ProviderAppData(BaseModel):
    """Application databag model for the provider side of the prometheus_remote_write interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {'alert_rules_encodings': '["lzma", "json"]'},
                {
                    'alert_rules_encodings': '["lzma", "json"]',
                    'event': '{"errors": "error validating rule: could not parse expression"}',
                },
            ]
        }
    )

    alert_rules_encodings: Json[list[Literal['json', 'lzma']]] | None = Field(
        default=None,
        description='The encodings that the provider can read the requirer\'s `alert_rules` in, as a JSON list. `json` is a plain JSON object, and `lzma` is the same object LZMA-compressed and base64-encoded. A provider that does not set this is assumed to read only `json`.',
        examples=['["lzma", "json"]'],
    )
    event: Json[Event] | None = Field(
        default=None,
        description='Feedback to the requirer about the alert rules it published, as a JSON object.',
        examples=['{"errors": "error validating rule: could not parse expression"}', '{}'],
    )


class ProviderUnitData(BaseModel):
    """Unit databag model for the provider side of the prometheus_remote_write interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {'remote_write': '{"url": "http://192.168.1.2:9090/api/v1/write"}'},
                {
                    'remote_write': '{"url": "http://prometheus-k8s-0.prometheus-k8s-endpoints.cos.svc.cluster.local:9090/api/v1/write"}'
                },
            ]
        }
    )

    remote_write: Json[RemoteWrite] = Field(
        description='The remote write endpoint of the unit, as a JSON object.',
        examples=['{"url": "http://192.168.1.2:9090/api/v1/write"}'],
    )


class RequirerAppData(BaseModel):
    """Application databag model for the requirer side of the prometheus_remote_write interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [{'alert_rules': _JSON_RULES}, {'alert_rules': _LZMA_RULES}]
        }
    )

    alert_rules: Json[AlertRules | CompressedAlertRules] | CompressedAlertRules = Field(
        description='The requirer\'s alert and recording rules, in the format of a Prometheus rule file. The value is either a JSON object, or, if the provider advertises the `lzma` encoding, the same JSON LZMA-compressed and base64-encoded, which keeps large rule sets below the Juju relation data size limit. Compressed rules can be read with `<value> | base64 -d | xz -d | jq`.',
        examples=['{}', _LZMA_RULES],
    )
    scrape_metadata: str | None = Field(
        default=None,
        description='The Juju topology of the requirer, as a JSON object. The provider uses it to name the alert rules if the rules have no topology labels.',
        examples=[
            '{"model": "some-model", "model_uuid": "00000000-0000-0000-0000-000000000000", "application": "consumer-charm", "charm_name": "consumer-charm"}'
        ],
    )


RequirerUnitData = None
