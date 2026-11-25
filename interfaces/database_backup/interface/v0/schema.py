"""This file defines the schemas for the provider and requirer sides of the database_backup interface."""

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class _BareStringDatabag(BaseModel):
    """Base class for databag models that don't strictly JSON encode all entries."""

    @staticmethod
    def __juju_decoder__(value: str) -> str:
        """Pass Juju's string through unmodified to be decoded by individual field validators."""
        return value

    @staticmethod
    def __juju_encoder__(value: str | None) -> str:
        """Convert `None` to "", erasing the value; Ops will error on a non-string."""
        return "" if value is None else value


class S3StorageConfig(BaseModel):
    """The S3 storage to use for a job, with the same fields as the s3 v0 provider databag."""

    model_config = ConfigDict(populate_by_name=True)

    bucket: str = Field(
        description="The bucket to store the backups in, or to retrieve them from.",
        examples=["my-bucket"],
        title="Bucket name",
    )

    access_key: str = Field(
        alias="access-key",
        description="The access key for connecting to the object storage.",
        examples=["access-key"],
        title="Access key",
    )

    secret_key: str = Field(
        alias="secret-key",
        description="The secret key for connecting to the object storage.",
        examples=["secret-key"],
        title="Secret key",
    )

    path: str | None = Field(
        default=None,
        description="The path inside the bucket to store objects.",
        examples=["backups/mysql/"],
        title="Path",
    )

    endpoint: str | None = Field(
        default=None,
        description="The endpoint used to connect to the object storage.",
        examples=["https://s3.example.com/"],
        title="Endpoint URL",
    )

    region: str | None = Field(
        default=None,
        description="The region used to connect to the object storage.",
        examples=["us-east-1"],
        title="Region",
    )

    s3_uri_style: str | None = Field(
        default=None,
        alias="s3-uri-style",
        description="The S3 protocol specific bucket path lookup type.",
        examples=["path", "host"],
        title="S3 URI style",
    )

    storage_class: str | None = Field(
        default=None,
        alias="storage-class",
        description="The storage class for objects uploaded to the object storage.",
        examples=["glacier"],
        title="Storage class",
    )

    tls_ca_chain: list[str] | None = Field(
        default=None,
        alias="tls-ca-chain",
        description="The complete CA chain, which can be used for HTTPS validation.",
        examples=[["-----BEGIN CERTIFICATE-----\nMIIB...\n-----END CERTIFICATE-----"]],
        title="TLS CA chain",
    )

    s3_api_version: Literal[2, 4] | None = Field(
        default=None,
        alias="s3-api-version",
        description="The S3 protocol specific API signature version.",
        examples=[2, 4],
        title="S3 API signature",
    )

    attributes: list[str] | None = Field(
        default=None,
        description="The custom metadata (HTTP headers).",
        examples=[["Cache-Control=max-age=90000,min-fresh=9000"]],
        title="Custom metadata",
    )


class JobConfig(BaseModel):
    """The configuration of a job."""

    model_config = ConfigDict(extra="forbid")

    compression: bool = Field(
        description="Whether the backups are compressed.",
        examples=[True, False],
        title="Compression",
    )


class RequestedJob(BaseModel):
    """A backup or restore job requested by the requirer."""

    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(
        alias="job-id",
        description="A unique ID for the job.",
        examples=["job-01693ed2-644f-11ed-81ce-0242ac120001"],
        title="Job ID",
    )

    job_type: Literal["backup", "restore"] = Field(
        alias="job-type",
        description="Whether to back up or to restore.",
        examples=["backup", "restore"],
        title="Job type",
    )

    job_config: JobConfig = Field(
        alias="job-config",
        description="The job configuration.",
        examples=[{"compression": True}],
        title="Job config",
    )

    storage_interface: Literal["s3"] = Field(
        alias="storage-interface",
        description="The storage interface to use for storing or retrieving files.",
        examples=["s3"],
        title="Storage interface",
    )

    storage_config: S3StorageConfig = Field(
        alias="storage-config",
        description="The storage to use for the job.",
        examples=[{"bucket": "my-bucket", "access-key": "access-key", "secret-key": "secret-key"}],
        title="Storage config",
    )

    artefact_path: str | None = Field(
        default=None,
        alias="artefact-path",
        description="For a restore, where to retrieve the backup files from.",
        examples=["/path/to/retrieve/backups/"],
        title="Artefact path",
    )


class JobResult(BaseModel):
    """The status of a job that the provider is running or has run."""

    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(
        alias="job-id",
        description="The ID of the job, the same as the one the requirer gave.",
        examples=["job-01693ed2-644f-11ed-81ce-0242ac120001"],
        title="Job ID",
    )

    job_type: Literal["backup", "restore"] = Field(
        alias="job-type",
        description="The job type, the same as the one the requirer gave.",
        examples=["backup", "restore"],
        title="Job type",
    )

    job_config: JobConfig | None = Field(
        default=None,
        alias="job-config",
        description="The job configuration.",
        examples=[{"compression": True}],
        title="Job config",
    )

    storage_interface: Literal["s3"] = Field(
        alias="storage-interface",
        description="The storage interface used for storing or retrieving files.",
        examples=["s3"],
        title="Storage interface",
    )

    storage_config: S3StorageConfig = Field(
        alias="storage-config",
        description="The storage used for the job.",
        examples=[{"bucket": "my-bucket", "access-key": "access-key", "secret-key": "secret-key"}],
        title="Storage config",
    )

    status: Literal["running", "success", "error"] = Field(
        description="The status of the job.",
        examples=["running", "success", "error"],
        title="Job status",
    )

    message: str | None = Field(
        default=None,
        description="A message describing the status of the job, such as an error message.",
        examples=["MySQL charm in blocked state"],
        title="Job message",
    )

    artefact_path: str | None = Field(
        default=None,
        alias="artefact-path",
        description="The artefact path for the job. This is where the backup files and logs are stored.",
        examples=["/path/to/artefacts/"],
        title="Artefact path",
    )


_REQUESTED_JOBS_EXAMPLE = [
    {
        "job-id": "job-01693ed2-644f-11ed-81ce-0242ac120001",
        "job-type": "backup",
        "job-config": {"compression": True},
        "storage-interface": "s3",
        "storage-config": {"bucket": "my-bucket", "access-key": "access-key", "secret-key": "secret-key"},
    },
    {
        "job-id": "job-ad989f5a-6453-11ed-81ce-0242ac120003",
        "job-type": "restore",
        "job-config": {"compression": False},
        "storage-interface": "s3",
        "storage-config": {"bucket": "my-bucket", "access-key": "access-key", "secret-key": "secret-key"},
        "artefact-path": "/path/to/retrieve/backups/",
    },
]

_JOB_RESULTS_EXAMPLE = [
    {
        "job-id": "job-01693ed2-644f-11ed-81ce-0242ac120001",
        "job-type": "backup",
        "job-config": {"compression": True},
        "storage-interface": "s3",
        "storage-config": {"bucket": "my-bucket", "access-key": "access-key", "secret-key": "secret-key"},
        "status": "success",
        "artefact-path": "/path/to/backup/",
    },
    {
        "job-id": "job-ad989f5a-6453-11ed-81ce-0242ac120003",
        "job-type": "restore",
        "job-config": {"compression": False},
        "storage-interface": "s3",
        "storage-config": {"bucket": "my-bucket", "access-key": "access-key", "secret-key": "secret-key"},
        "status": "error",
        "message": "MySQL charm in blocked state",
    },
]


class ProviderUnitData(_BareStringDatabag):
    """The provider's unit databag: the jobs that this unit has run or is running."""

    model_config = ConfigDict(
        strict=True,
        json_schema_extra={"examples": [{"jobs": json.dumps(_JOB_RESULTS_EXAMPLE)}]},
    )

    jobs: list[JobResult] = Field(
        description="The current or most recently completed jobs run by this unit. A JSON array on the wire.",
        examples=[_JOB_RESULTS_EXAMPLE[:1]],
        title="Jobs",
    )

    @field_validator("jobs", mode="before")
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value  # __init__ argument was already deserialized.
        return json.loads(value)

    @field_serializer("jobs")
    def _dump_json(self, value: list[JobResult]) -> str:
        return json.dumps([job.model_dump(by_alias=True, exclude_none=True) for job in value])


class RequirerAppData(_BareStringDatabag):
    """The requirer's application databag: the jobs that it wants run."""

    model_config = ConfigDict(
        strict=True,
        json_schema_extra={"examples": [{"jobs": json.dumps(_REQUESTED_JOBS_EXAMPLE)}]},
    )

    jobs: list[RequestedJob] = Field(
        description="The backup and restore jobs to run. A JSON array on the wire.",
        examples=[_REQUESTED_JOBS_EXAMPLE[:1]],
        title="Jobs",
    )

    @field_validator("jobs", mode="before")
    @classmethod
    def _load_json(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value  # __init__ argument was already deserialized.
        return json.loads(value)

    @field_serializer("jobs")
    def _dump_json(self, value: list[RequestedJob]) -> str:
        return json.dumps([job.model_dump(by_alias=True, exclude_none=True) for job in value])


ProviderAppData = None
RequirerUnitData = None
