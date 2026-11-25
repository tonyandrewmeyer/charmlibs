# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""This file defines the schemas for the provider and requirer sides of the cos_agent interface."""

import base64
import json
import lzma
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    Json,
    PlainSerializer,
    WithJsonSchema,
)

_DASHBOARD = (
    '/Td6WFoAAATm1rRGAgAhARQAAAD/5+wJ4ABSAEhdAD2IiobUVOndN3jT8g7f/wy5Iv4mALoZnNBKF3Zbl05h'
    'bCq7/TQMxp2U26ZlkkT5LdnOpK8iruD85s/0K20znur5LjYnRbHbAAD0GexJReZchgABZFPGG3XTH7bzfQEAAAAABFla'
)
_ALERT_RULES = (
    '{"groups": [{"name": "db_58b48ff0_zookeeper_HostHealth_rules", "rules": [{"alert": "HostDown", '
    '"expr": "up < 1", "for": "5m", "labels": {"severity": "critical", "juju_model": "db", '
    '"juju_model_uuid": "58b48ff0-608b-435f-83b9-ea643e0b98db", "juju_application": "zookeeper", '
    '"juju_charm": "zookeeper"}, "annotations": {"summary": "Host {{ $labels.instance }} is down."}}]}]}'
)
_SCRAPE_JOBS = (
    '[{"metrics_path": "/metrics", "static_configs": [{"targets": ["localhost:9100"]}], '
    '"job_name": "zookeeper_default_1a2b3c4d"}]'
)


def _serialize_grafana_dashboard(raw_json: str | bytes) -> "GrafanaDashboard":
    if not isinstance(raw_json, bytes):
        raw_json = raw_json.encode("utf-8")
    encoded = base64.b64encode(lzma.compress(raw_json)).decode("utf-8")
    return GrafanaDashboard(encoded)


# custom data type, pydantic 2
GrafanaDashboard = Annotated[
    str,
    AfterValidator(
        lambda x: json.loads(lzma.decompress(base64.b64decode(x.encode("utf-8"))).decode())
    ),
    PlainSerializer(lambda x: _serialize_grafana_dashboard(json.dumps(x)), return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization'),
]


class NestedDataModel(BaseModel):
    """The provider's telemetry configuration, JSON-encoded in the `config` field."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    metrics_alert_rules: dict = Field(
        description="The Prometheus alert rules, as rule groups, with the principal's Juju topology applied.",
        examples=[json.loads(_ALERT_RULES)],
    )
    log_alert_rules: dict = Field(
        description="The Loki alert rules, as rule groups, with the principal's Juju topology applied.",
        examples=[{"groups": []}],
    )
    dashboards: list[GrafanaDashboard] = Field(
        description="The Grafana dashboards. Each dashboard is JSON-encoded, LZMA-compressed, and then base64-encoded.",
        examples=[[_DASHBOARD]],
    )
    subordinate: bool | None = Field(
        default=None,
        description="No longer used. The library writes `null`.",
        examples=[None],
    )
    metrics_scrape_jobs: list[dict] = Field(
        description="The Prometheus scrape configurations for the requirer to scrape. "
        "Targets on `localhost` are on the principal's machine.",
        examples=[json.loads(_SCRAPE_JOBS)],
    )
    log_slots: list[str] = Field(
        description='The snap slots to connect to for reading logs. Each slot is in the form "snap-name:slot".',
        examples=[["charmed-zookeeper:logs"]],
    )
    tracing_protocols: list[str] | None = Field(
        default=None,
        description="The tracing protocols that the provider wants receivers for, such as `otlp_http` or `otlp_grpc`.",
        examples=[["otlp_http", "otlp_grpc"]],
    )


class ProviderUnitData(BaseModel):
    """Unit databag model for the provider (principal) side of the cos_agent interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'config': '{"metrics_alert_rules": '
                    + _ALERT_RULES
                    + ', "log_alert_rules": {"groups": []}, "dashboards": ["'
                    + _DASHBOARD
                    + '"], "subordinate": null, "metrics_scrape_jobs": '
                    + _SCRAPE_JOBS
                    + ', "log_slots": ["charmed-zookeeper:logs"], "tracing_protocols": ["otlp_http"]}',
                },
            ]
        }
    )

    config: Json[NestedDataModel] = Field(
        description="The provider's telemetry configuration: alert rules, dashboards, scrape jobs, log slots, "
        "and requested tracing protocols.",
        examples=[
            '{"metrics_alert_rules": {"groups": []}, "log_alert_rules": {"groups": []}, "dashboards": [], '
            '"subordinate": null, "metrics_scrape_jobs": [], "log_slots": [], "tracing_protocols": null}'
        ],
    )


class ProtocolType(BaseModel):
    """A tracing receiver protocol."""

    name: str = Field(
        description="The receiver protocol name.",
        examples=["otlp_grpc", "otlp_http"],
    )
    type: Literal["http", "grpc"] = Field(
        description="The transport protocol that the receiver uses.",
        examples=["http", "grpc"],
    )


class Receiver(BaseModel):
    """A tracing receiver that the requirer has enabled."""

    protocol: ProtocolType = Field(
        description="The receiver protocol name and type.",
        examples=[{"name": "otlp_http", "type": "http"}],
    )
    url: str | None = Field(
        description="The URL at which the receiver is reachable, or `null` if the requirer can't forward traces yet. "
        "For gRPC protocols, the URL has no scheme.",
        examples=["http://zookeeper-0.lxd:4318", "zookeeper-0.lxd:4317", None],
    )


class RequirerUnitData(BaseModel):
    """Unit databag model for the requirer (subordinate) side of the cos_agent interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'receivers': '[{"protocol": {"name": "otlp_grpc", "type": "grpc"}, "url": "zookeeper-0.lxd:4317"}, '
                    '{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://zookeeper-0.lxd:4318"}]',
                },
                {
                    'receivers': '[{"protocol": {"name": "otlp_http", "type": "http"}, "url": null}]',
                },
                {
                    'receivers': '[]',
                },
            ]
        }
    )

    receivers: Json[list[Receiver]] = Field(
        description="The tracing receivers for the protocols that the related principals requested, sorted by protocol name.",
        examples=[
            '[{"protocol": {"name": "otlp_http", "type": "http"}, "url": "http://zookeeper-0.lxd:4318"}]'
        ],
    )


ProviderAppData = None
RequirerAppData = None
