"""This file defines the schemas for the provider and requirer sides of the grafana_datasource interface."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, Json


class GrafanaSourceData(BaseModel):
    """Information about the provider's datasource."""

    model: str = Field(
        description="Name of the Juju model where the source is deployed.", examples=['cos']
    )
    model_uuid: str = Field(
        description="UUID of the Juju model where the source is deployed.",
        examples=["f4d59020-c8e7-4053-8044-a2c1e5591c7f"],
    )
    application: str = Field(
        description="Name of the Juju application that is the source.",
        examples=['tempo', 'loki', 'prometheus'],
    )
    type: str = Field(
        description="Type of the datasource. For the possible values, see "
        "https://grafana.com/docs/grafana/latest/datasources/#built-in-core-data-sources.",
        examples=['tempo', 'loki', 'prometheus'],
    )
    extra_fields: Any | None = Field(
        default=None,
        description="Any datasource-type-specific additional configuration. Maps to the datasource's `jsonData`.",
        examples=[{"httpMethod": "POST"}, None],
    )
    secure_extra_fields: Any | None = Field(
        default=None,
        description="Any secure datasource-type-specific additional configuration. Maps to the datasource's `secureJsonData`.",
        examples=[{"password": "secret"}, None],
    )


class ProviderAppData(BaseModel):
    """Application databag model for the provider side of this interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'grafana_source_data': '{"model": "cos", "model_uuid": "f4d59020-c8e7-4053-8044-a2c1e5591c7f", '
                    '"application": "tempo", "type": "tempo", "extra_fields": null, "secure_extra_fields": null}',
                    'grafana_source_app_host': 'http://tempo.cos.svc.cluster.local:3200',
                },
                {
                    'grafana_source_data': '{"model": "cos", "model_uuid": "f4d59020-c8e7-4053-8044-a2c1e5591c7f", '
                    '"application": "prometheus", "type": "prometheus", "extra_fields": {"httpMethod": "POST"}, '
                    '"secure_extra_fields": null}',
                },
            ]
        }
    )

    grafana_source_data: Json[GrafanaSourceData] = Field(
        description="Information about the datasource.",
        examples=[
            '{"model": "cos", "model_uuid": "f4d59020-c8e7-4053-8044-a2c1e5591c7f", "application": "tempo", '
            '"type": "tempo", "extra_fields": null, "secure_extra_fields": null}'
        ],
    )
    grafana_source_app_host: str | None = Field(
        default=None,
        description="The URL of a single datasource for the whole application, such as a load-balanced or ingress address. "
        "If it has no scheme, `http://` is assumed.",
        examples=[
            'http://tempo.cos.svc.cluster.local:3200',
            'https://example.com/cos-mimir/prometheus',
        ],
    )


class ProviderUnitData(BaseModel):
    """Unit databag model for the provider side of this interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'grafana_source_host': 'http://prometheus-0.prometheus-endpoints.cos.svc.cluster.local:9090'
                },
                {},
            ]
        }
    )

    grafana_source_host: str | None = Field(
        default=None,
        description="The URL of this unit's datasource. If it has no scheme, `http://` is assumed.",
        examples=[
            'http://prometheus-0.prometheus-endpoints.cos.svc.cluster.local:9090',
            'localhost:80',
        ],
    )


class RequirerAppData(BaseModel):
    """Application databag model for the requirer side of this interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'grafana_uid': 'f4d59020-c8e7-4053-8044-a2c1e5591c7f-grafana',
                    'datasource_uids': '{"prometheus/0": "juju_cos_f4d59020-c8e7-4053-8044-a2c1e5591c7f_prometheus_0", '
                    '"prometheus/1": "juju_cos_f4d59020-c8e7-4053-8044-a2c1e5591c7f_prometheus_1"}',
                    'grafana_base_url': 'http://grafana-0.grafana-endpoints.cos.svc.cluster.local:3000',
                },
                {
                    'grafana_uid': 'f4d59020-c8e7-4053-8044-a2c1e5591c7f-grafana',
                    'datasource_uids': '{}',
                    'grafana_base_url': 'https://example.com/cos-grafana',
                    'app_datasource_uid': 'juju_cos_f4d59020-c8e7-4053-8044-a2c1e5591c7f_tempo',
                },
            ]
        }
    )

    datasource_uids: Json[dict[str, str]] = Field(
        description="The UID of each unit's datasource, by provider unit name.",
        examples=['{"tempo/0": "juju_cos_f4d59020-c8e7-4053-8044-a2c1e5591c7f_tempo_0"}'],
    )
    grafana_uid: str = Field(
        description="UID of the requirer application.",
        examples=['f4d59020-c8e7-4053-8044-a2c1e5591c7f-grafana'],
    )
    grafana_base_url: str | None = Field(
        default=None,
        description="Base URL of the requirer application, which may be ingressed.",
        examples=['http://grafana.example.com/cos-grafana'],
    )
    app_datasource_uid: str | None = Field(
        default=None,
        description="The UID of the datasource for the whole application, if the provider set `grafana_source_app_host`.",
        examples=['juju_cos_f4d59020-c8e7-4053-8044-a2c1e5591c7f_tempo'],
    )


RequirerUnitData = None
