# Copyright 2025 Canonical
# See LICENSE file for licensing details.


from pydantic import BaseModel, ConfigDict, Field, Json


class VeleroBackupSpec(BaseModel):
    """Pydantic model for the backup specification details."""

    include_namespaces: list[str] | None = Field(
        None,
        description="Namespaces to include in the backup. If not set, all namespaces are included.",
        title="Included Namespaces",
        examples=[["kubeflow"]],
    )
    include_resources: list[str] | None = Field(
        None,
        description="Resource kinds to include in the backup. If not set, all resource kinds are included.",
        title="Included Resources",
        examples=[["profiles.kubeflow.org", "deployments"]],
    )
    exclude_namespaces: list[str] | None = Field(
        None,
        description="Namespaces to exclude from the backup.",
        title="Excluded Namespaces",
        examples=[["default"]],
    )
    exclude_resources: list[str] | None = Field(
        None,
        description="Resource kinds to exclude from the backup.",
        title="Excluded Resources",
        examples=[["pods"]],
    )
    label_selector: dict[str, str] | None = Field(
        None,
        description="Labels that a resource must have to be included in the backup.",
        title="Label Selector",
        examples=[{"app.kubernetes.io/name": "mlmd"}],
    )
    ttl: str | None = Field(
        None,
        description="How long to keep the backup, as a duration in hours, minutes, and seconds. If not set, Velero's default is used.",
        title="Backup TTL",
        examples=["24h", "72h30m"],
    )
    include_cluster_resources: bool | None = Field(
        None,
        description="Whether to include cluster-scoped resources in the backup. If not set, Velero decides based on the other filters.",
        title="Include Cluster Resources",
        examples=[True],
    )
    schedule: str | None = Field(
        None,
        description="A cron expression for scheduled backups. If not set, backups are only made on demand.",
        title="Schedule",
        examples=["0 2 * * *"],
    )
    paused: bool | None = Field(
        None,
        description="Whether the schedule is paused. Only used when `schedule` is set.",
        title="Paused",
        examples=[False],
    )
    skip_immediately: bool | None = Field(
        None,
        description="Whether to skip the backup that would otherwise be made as soon as the schedule is created. Only used when `schedule` is set.",
        title="Skip Immediately",
        examples=[False],
    )
    use_owner_references_in_backup: bool | None = Field(
        None,
        description="Whether backups made by the schedule are owned by the schedule, so that they're removed when it is. Only used when `schedule` is set.",
        title="Use Owner References in Backup",
        examples=[False],
    )


class ProviderAppData(BaseModel):
    """Pydantic model for the provider's application databag."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "app": "kubeflow-profiles",
                    "relation_name": "profiles-backup-config",
                    "model": "kubeflow",
                    "spec": '{"include_namespaces":["kubeflow"],"include_resources":["profiles.kubeflow.org"],"exclude_namespaces":null,"exclude_resources":null,"label_selector":{"app":"kubeflow"},"ttl":null,"include_cluster_resources":false,"schedule":null,"paused":null,"skip_immediately":null,"use_owner_references_in_backup":null}',
                },
                {
                    "app": "my-app",
                    "relation_name": "backup",
                    "model": "my-model",
                    "spec": '{"include_namespaces":["my-namespace"],"include_resources":null,"exclude_namespaces":null,"exclude_resources":null,"label_selector":null,"ttl":"24h","include_cluster_resources":null,"schedule":"0 2 * * *","paused":false,"skip_immediately":false,"use_owner_references_in_backup":false}',
                },
            ]
        }
    )

    app: str = Field(
        ...,
        description="Name of the client application requesting the backup.",
        title="Client Application Name",
        examples=["kubeflow-profiles"],
    )
    relation_name: str = Field(
        ...,
        description="Name of the endpoint on the client application that this relation uses.",
        title="Client Relation Name",
        examples=["profiles-backup-config"],
    )
    model: str = Field(
        ...,
        description="Name of the model that the client application is in.",
        title="Client Model Name",
        examples=["kubeflow"],
    )
    spec: Json[VeleroBackupSpec] = Field(
        ...,
        description="What to back up, as a JSON object.",
        title="Velero Backup Spec",
        examples=[
            '{"include_namespaces":["kubeflow"],"include_resources":["profiles.kubeflow.org"]}'
        ],
    )


ProviderUnitData = None
RequirerAppData = None
RequirerUnitData = None
