"""This file defines the schemas for both sides of the grafana_datasource_exchange interface."""

from pydantic import BaseModel, ConfigDict, Field, Json


class GrafanaDatasource(BaseModel):
    """A datasource that Grafana has assigned a UID to."""

    type: str = Field(
        description="Type of the datasource, typically one of "
        "https://grafana.com/docs/grafana/latest/datasources/#built-in-core-data-sources.",
        examples=["tempo", "loki", "prometheus", "elasticsearch"],
    )
    uid: str = Field(
        description="Grafana datasource UID, as assigned by Grafana.",
        examples=["juju_cos_f4d59020-c8e7-4053-8044-a2c1e5591c7f_loki_0"],
    )
    grafana_uid: str = Field(
        description="The UID of the Grafana application that assigned the datasource UID.",
        examples=["f4d59020-c8e7-4053-8044-a2c1e5591c7f-grafana"],
    )


class GrafanaSourceAppData(BaseModel):
    """Application databag model for both sides of this interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'datasources': '[{"type": "loki", "uid": "juju_cos_f4d59020-c8e7-4053-8044-a2c1e5591c7f_loki_0", '
                    '"grafana_uid": "f4d59020-c8e7-4053-8044-a2c1e5591c7f-grafana"}, '
                    '{"type": "loki", "uid": "juju_cos_f4d59020-c8e7-4053-8044-a2c1e5591c7f_loki_1", '
                    '"grafana_uid": "f4d59020-c8e7-4053-8044-a2c1e5591c7f-grafana"}]',
                },
                {'datasources': '[]'},
            ]
        }
    )

    datasources: Json[list[GrafanaDatasource]] = Field(
        description="The datasources that this application's data can be queried in, sorted by `uid`.",
        examples=[
            '[{"type": "tempo", "uid": "juju_cos_f4d59020-c8e7-4053-8044-a2c1e5591c7f_tempo_0", '
            '"grafana_uid": "f4d59020-c8e7-4053-8044-a2c1e5591c7f-grafana"}]'
        ],
    )


ProviderAppData = GrafanaSourceAppData
ProviderUnitData = None
RequirerAppData = GrafanaSourceAppData
RequirerUnitData = None
