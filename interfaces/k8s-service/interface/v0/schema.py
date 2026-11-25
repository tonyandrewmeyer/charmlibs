"""This file defines the schemas for the provider and requirer sides of the k8s-service interface.

There are two formats in use. Charms that use `serialized-data-interface`
(SDI) write `_supported_versions` and a YAML-encoded `data`. Charms that
use the `k8s_service_info` library write `name` and `port`.
"""

from pydantic import BaseModel, ConfigDict, Field

_SUPPORTED_VERSIONS_DESCRIPTION = (
    'The SDI schema versions that this side supports, as a YAML-encoded list.'
    ' Only `v1` exists. Only written by charms that use SDI.'
)


class ProviderAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    '_supported_versions': '- v1\n',
                    'data': "service-name: kfp-api.kubeflow\nservice-port: '8888'\n",
                },
                {
                    'name': 'metadata-grpc-service',
                    'port': '8080',
                },
            ]
        }
    )

    supported_versions: str | None = Field(
        default=None,
        alias='_supported_versions',
        description=_SUPPORTED_VERSIONS_DESCRIPTION,
        title='Supported versions',
        examples=['- v1\n'],
    )
    data: str | None = Field(
        default=None,
        description=(
            'The Kubernetes Service, as a YAML-encoded mapping with `service-name`, the name of'
            ' the Service (for example, `kfp-api.kubeflow`), and `service-port`, its port as a'
            ' string. Only written by charms that use SDI.'
        ),
        title='Service data',
        examples=["service-name: kfp-api.kubeflow\nservice-port: '8888'\n"],
    )
    name: str | None = Field(
        default=None,
        description=(
            'The name of the Kubernetes Service, as it is in the resource metadata.'
            ' Only written by charms that use the `k8s_service_info` library.'
        ),
        title='Service name',
        examples=['metadata-grpc-service'],
    )
    port: str | None = Field(
        default=None,
        description=(
            'The port of the Kubernetes Service.'
            ' Only written by charms that use the `k8s_service_info` library.'
        ),
        title='Service port',
        examples=['8080'],
    )


class RequirerAppData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    '_supported_versions': '- v1\n',
                },
            ]
        }
    )

    supported_versions: str | None = Field(
        default=None,
        alias='_supported_versions',
        description=_SUPPORTED_VERSIONS_DESCRIPTION,
        title='Supported versions',
        examples=['- v1\n'],
    )


ProviderUnitData = None
RequirerUnitData = None
