# Copyright 2024 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the dns_record interface.

It defines two models, `ProviderAppData` and `RequirerAppData`.
"""

import ipaddress
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, Json, field_validator, model_validator


class Status(str, Enum):
    """Represent the status values."""

    APPROVED = "approved"
    PERMISSION_DENIED = "permission_denied"
    CONFLICT = "conflict"
    INVALID_DATA = "invalid_data"
    FAILURE = "failure"
    UNKNOWN = "unknown"
    PENDING = "pending"


class RecordType(str, Enum):
    """Represent the DNS record types."""

    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    DKIM = "DKIM"
    SPF = "SPF"
    DMARC = "DMARC"
    TXT = "TXT"
    CAA = "CAA"
    SRV = "SRV"
    SVCB = "SVCB"
    HTTPS = "HTTPS"
    PTR = "PTR"
    SOA = "SOA"
    NS = "NS"
    DS = "DS"
    DNSKEY = "DNSKEY"


class RecordClass(str, Enum):
    """Represent the DNS record classes."""

    IN = "IN"


class DnsProviderData(BaseModel):
    """The status of one DNS record requested by the requirer."""

    uuid: UUID = Field(
        title="UUID",
        description="The UUID of the requirer's DNS entry that this status is for.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    status: Status = Field(
        title="Status",
        description=(
            "The status of the request for the DNS record: `approved` (the record is served), "
            "`pending` (waiting for review or for an upstream provider), `permission_denied` "
            "(the requirer isn't allowed this record), `conflict` (another request is for the "
            "same name, class and type), `invalid_data` (the request isn't valid), `failure` "
            "(creating the record failed), or `unknown`."
        ),
        examples=[Status.APPROVED, Status.PERMISSION_DENIED],
    )
    description: str | None = Field(
        default=None,
        title="Status description",
        description="A human-readable explanation of the status.",
        examples=["Waiting for review"],
    )


class ProviderAppData(BaseModel):
    """The statuses of the DNS records requested by the requirer."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "dns_entries": (
                        '[{"uuid": "550e8400-e29b-41d4-a716-446655440002", '
                        '"status": "permission_denied", '
                        '"description": "Denied by the DNS policy"}, '
                        '{"uuid": "550e8400-e29b-41d4-a716-446655440003", '
                        '"status": "approved"}]'
                    ),
                    "ddns-domain": "1403f42c.example.com",
                },
            ]
        },
    )

    dns_entries: Json[list[DnsProviderData]] = Field(
        title="DNS entries",
        description=(
            "A JSON-encoded list of the statuses of the DNS records requested by the requirer."
        ),
        examples=['[{"uuid": "550e8400-e29b-41d4-a716-446655440003", "status": "approved"}]'],
    )
    ddns_domain: str | None = Field(
        default=None,
        alias="ddns-domain",
        title="Automatically allocated domain",
        description=(
            "A domain that the provider allocated for the requirer, and that resolves to the "
            "requirer's addresses."
        ),
        examples=["1403f42c.example.com"],
    )


class RequirerEntries(BaseModel):
    """One DNS record requested by the requirer."""

    domain: str = Field(
        min_length=1,
        title="Domain",
        description="The domain (zone) that the record is in.",
        examples=["cloud.canonical.com", "staging.ubuntu.com"],
    )
    host_label: str = Field(
        min_length=1,
        title="Host label",
        description="The host label of the record within the domain.",
        examples=["admin", "www"],
    )
    ttl: int | None = Field(
        default=None,
        title="TTL",
        description="The DNS time to live, in seconds.",
        examples=["600", "1200"],
    )
    record_class: RecordClass | None = Field(
        default=None,
        title="Record class",
        description="The DNS record class.",
        examples=[RecordClass.IN],
    )
    record_type: RecordType | None = Field(
        default=None,
        title="Record type",
        description="The DNS record type.",
        examples=[RecordType.A, RecordType.CNAME],
    )
    record_data: str = Field(
        min_length=1,
        title="Record data",
        description=(
            "The DNS record value. For `A` and `AAAA` records, it is an IP address; "
            "for other record types, it is the value in zone file syntax."
        ),
        examples=["91.189.91.47", "www.example.com."],
    )
    uuid: UUID = Field(
        title="UUID",
        description=(
            "A UUID that identifies this entry, and that the provider uses to report its status."
        ),
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    @model_validator(mode="after")
    def _check_address_record_data(self) -> "RequirerEntries":
        if self.record_type in (RecordType.A, RecordType.AAAA):
            ipaddress.ip_address(self.record_data)
        return self


class RequirerAppData(BaseModel):
    """The DNS records for the provider to manage."""

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "dns_entries": (
                        '[{"uuid": "550e8400-e29b-41d4-a716-446655440002", '
                        '"domain": "cloud.canonical.com", "host_label": "admin", '
                        '"ttl": "600", "record_class": "IN", "record_type": "A", '
                        '"record_data": "91.189.91.48"}, '
                        '{"uuid": "550e8400-e29b-41d4-a716-446655440003", '
                        '"domain": "staging.canonical.com", "host_label": "www", '
                        '"ttl": "600", "record_class": "IN", "record_type": "CNAME", '
                        '"record_data": "admin.cloud.canonical.com."}]'
                    ),
                    "ddns-addresses": "91.189.91.48,2620:2d:4000:1::27",
                },
            ]
        },
    )

    dns_entries: Json[list[RequirerEntries]] = Field(
        title="DNS entries",
        description="A JSON-encoded list of the DNS records for the provider to manage.",
        examples=[
            '[{"uuid": "550e8400-e29b-41d4-a716-446655440003", "domain": "staging.canonical.com", '
            '"host_label": "www", "ttl": "600", "record_class": "IN", "record_type": "A", '
            '"record_data": "91.189.91.47"}]'
        ],
    )
    ddns_addresses: str | None = Field(
        default=None,
        alias="ddns-addresses",
        title="Automatically allocated domain addresses",
        description=(
            "A comma-separated list of the IP addresses that the domain the provider allocated "
            "for the requirer resolves to. If it's not set, the provider uses the "
            "`ingress-address` of the requirer's units."
        ),
        examples=["91.189.91.48", "91.189.91.48,2620:2d:4000:1::27"],
    )

    @field_validator("ddns_addresses")
    @classmethod
    def _check_ddns_addresses(cls, value: str | None) -> str | None:
        if value is not None:
            for address in value.split(","):
                if address.strip():
                    ipaddress.ip_address(address.strip())
        return value


ProviderUnitData = None
RequirerUnitData = None
