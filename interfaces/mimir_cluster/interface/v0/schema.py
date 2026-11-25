"""This file defines the schemas for the provider and requirer sides of the mimir_cluster interface."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, Json, StringConstraints

_CA_CERT = '"-----BEGIN CERTIFICATE-----\\nMIIDdzCCAl+gAwIBAgIU...\\n-----END CERTIFICATE-----"'
_SERVER_CERT = (
    '"-----BEGIN CERTIFICATE-----\\nMIIDkjCCAnqgAwIBAgIU...\\n-----END CERTIFICATE-----"'
)


class ProviderAppData(BaseModel):
    """Application databag schema for the provider (coordinator) side of the mimir_cluster interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'worker_config': '"server:\\n  http_listen_port: 8080\\n  grpc_listen_port: 9095\\n"',
                },
                {
                    'worker_config': '"server:\\n  http_listen_port: 8080\\n  grpc_listen_port: 9095\\n"',
                    'loki_endpoints': '{"loki/0": "http://loki-0.loki-endpoints.cos.svc.cluster.local:3100/loki/api/v1/push"}',
                    'charm_tracing_receivers': '{"otlp_http": "http://tempo.cos.svc.cluster.local:4318"}',
                    'workload_tracing_receivers': '{"otlp_grpc": "tempo.cos.svc.cluster.local:4317"}',
                    'remote_write_endpoints': '[{"url": "http://mimir.cos.svc.cluster.local:8080/api/v1/push"}]',
                    'worker_ports': '[8080, 9095]',
                    'ca_cert': _CA_CERT,
                    'server_cert': _SERVER_CERT,
                    'privkey_secret_id': '"secret://f4d59020-c8e7-4053-8044-a2c1e5591c7f/d2v6qp7mp25c76r5slfg"',
                    's3_tls_ca_chain': _CA_CERT,
                    'worker_labels': '{"app.kubernetes.io/part-of": "mimir"}',
                },
            ]
        }
    )

    worker_config: Json[str] = Field(
        description='The Mimir configuration that the requirer should run with, YAML-encoded. '
        'It must conform to the schema that the deployed workload version supports; for example, see '
        'https://grafana.com/docs/mimir/latest/configure/configuration-parameters/.',
        examples=['"server:\\n  http_listen_port: 8080\\n  grpc_listen_port: 9095\\n"'],
    )
    loki_endpoints: Json[dict[str, str]] | None = Field(
        default=None,
        description='The loki_push_api endpoints to which the worker can push the logs it generates, by Loki unit name.',
        examples=[
            '{"loki/0": "http://loki-0.loki-endpoints.cos.svc.cluster.local:3100/loki/api/v1/push"}'
        ],
    )
    charm_tracing_receivers: Json[dict[str, str]] | None = Field(
        default=None,
        description='The endpoints to which the worker charm can push its charm traces, by protocol name, '
        'such as `otlp_http`.',
        examples=['{"otlp_http": "http://tempo.cos.svc.cluster.local:4318"}'],
    )
    workload_tracing_receivers: Json[dict[str, str]] | None = Field(
        default=None,
        description='The endpoints to which the workload can push its traces, by protocol name, '
        'such as `otlp_grpc`, `otlp_http`, or `jaeger_thrift_http`.',
        examples=['{"otlp_grpc": "tempo.cos.svc.cluster.local:4317"}'],
    )
    remote_write_endpoints: Json[list[dict[str, str]]] | None = Field(
        default=None,
        description='The endpoints to which the workload (and the worker charm) can push metrics. Each has a `url`.',
        examples=['[{"url": "http://mimir.cos.svc.cluster.local:8080/api/v1/push"}]'],
    )
    worker_ports: Json[list[int]] | None = Field(
        default=None,
        description='The ports that the worker should open, for its role. '
        'If this is not set, the worker opens all the ports that it used before this field was added.',
        examples=['[8080, 9095]'],
    )
    ca_cert: Json[str] | None = Field(
        default=None,
        description='The CA certificate for TLS encryption.',
        examples=[_CA_CERT],
    )
    server_cert: Json[str] | None = Field(
        default=None,
        description='The server certificate for TLS encryption.',
        examples=[_SERVER_CERT],
    )
    privkey_secret_id: Json[str] | None = Field(
        default=None,
        description='The ID of a Juju secret that holds the private key for TLS encryption, under the `private-key` key.',
        examples=['"secret://f4d59020-c8e7-4053-8044-a2c1e5591c7f/d2v6qp7mp25c76r5slfg"'],
    )
    s3_tls_ca_chain: Json[str] | None = Field(
        default=None,
        description='The CA chain to use to validate traffic with the S3 endpoint.',
        examples=[_CA_CERT],
    )
    worker_labels: Json[dict[str, str]] | None = Field(
        default=None,
        description='Extra labels for the worker pods, for the service mesh.',
        examples=['{"app.kubernetes.io/part-of": "mimir"}'],
    )


class _Topology(BaseModel):
    """Juju topology of a worker unit."""

    application: str = Field(
        description='The name of the worker application.',
        examples=['mimir-read'],
    )
    charm_name: str = Field(
        description='The name of the worker charm.',
        examples=['mimir-worker-k8s'],
    )
    unit: str = Field(
        description='The name of the worker unit.',
        examples=['mimir-read/0'],
    )


class RequirerUnitData(BaseModel):
    """Unit databag schema for the requirer (worker) side of the mimir_cluster interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'juju_topology': '{"application": "mimir-read", "unit": "mimir-read/0", "charm_name": "mimir-worker-k8s"}',
                    'address': '"mimir-read-0.mimir-read-endpoints.cos.svc.cluster.local"',
                },
            ]
        }
    )

    juju_topology: Json[_Topology] = Field(
        description='The Juju topology of the worker unit.',
        examples=[
            '{"application": "mimir-read", "unit": "mimir-read/0", "charm_name": "mimir-worker-k8s"}'
        ],
    )
    address: Json[str] = Field(
        description="The worker unit's FQDN.",
        examples=['"mimir-read-0.mimir-read-endpoints.cos.svc.cluster.local"'],
    )


Roles = Annotated[
    str,
    StringConstraints(
        pattern=r'^(all|read|write|backend|overrides-exporter|query-scheduler|flusher|query-frontend|querier|store-gateway|ingester|distributor|ruler|alertmanager|compactor)(,(all|read|write|backend|overrides-exporter|query-scheduler|flusher|query-frontend|querier|store-gateway|ingester|distributor|ruler|alertmanager|compactor))*$'
    ),
]


class RequirerAppData(BaseModel):
    """Application databag schema for the requirer (worker) side of the mimir_cluster interface."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {'role': '"all"'},
                {'role': '"backend"'},
                {'role': '"querier,query-frontend"'},
            ]
        }
    )

    role: Json[Roles] = Field(
        description='The roles that the worker application runs, separated by commas. Recent versions of the library sort them. '
        'The roles are `overrides-exporter`, `query-scheduler`, `flusher`, `query-frontend`, `querier`, `store-gateway`, '
        '`ingester`, `distributor`, `ruler`, `alertmanager`, and `compactor`, and the meta-roles `read`, `write`, `backend`, '
        'and `all`, which each stand for a set of roles.',
        examples=['"all"', '"querier,query-frontend"'],
    )


ProviderUnitData = None
