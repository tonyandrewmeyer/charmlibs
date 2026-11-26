# Copyright 2023 Canonical
# See LICENSE file for licensing details.
"""This file defines the schema for the provider side of the milter interface.

It defines one model, `ProviderUnitData`.
"""

from pydantic import BaseModel, ConfigDict, Field


class ProviderUnitData(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'port': '8892',
                },
            ]
        }
    )

    port: int = Field(
        ge=1,
        le=65536,
        description="The TCP port that the milter listens on, on this unit's ingress address.",
        title='Port',
        examples=['8892', '8893'],
    )


ProviderAppData = None
RequirerAppData = None
RequirerUnitData = None
