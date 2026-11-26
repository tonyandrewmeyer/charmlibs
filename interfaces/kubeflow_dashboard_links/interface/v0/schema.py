# Copyright 2023 Canonical
# See LICENSE file for licensing details.
"""This file defines the schemas for the provider and requirer sides of the kubeflow_dashboard_links interface."""

from pydantic import BaseModel, ConfigDict, Field, Json


class DashboardItem(BaseModel):
    """Representation of a Kubeflow Dashboard link entry.

    See https://www.kubeflow.org/docs/components/central-dash/customizing-menu/ for more details.
    """

    text: str = Field(
        description='The text shown for the link.',
        examples=['Experiments (KFP)'],
    )
    link: str = Field(
        description=(
            'Where the link goes: a relative link for the `menu` and `quick` locations,'
            ' or a full URL for the others.'
        ),
        examples=['/pipeline/#/experiments', 'https://charmed-kubeflow.io/docs'],
    )
    location: str = Field(
        description='Where the link is shown on the dashboard: `menu`, `external`, `quick`, or `documentation`.',
        examples=['menu', 'external', 'quick', 'documentation'],
    )
    icon: str = Field(
        default='icons:link',
        description=(
            'The icon for the link, from'
            ' [iron-icons](https://kevingleason.me/Polymer-Todo/bower_components/iron-icons/demo/index.html).'
        ),
        examples=['icons:link', 'done-all', 'kubeflow:pipeline-centered'],
    )
    type: str = Field(
        default='item',
        description='The type of the link entry, which is typically `item`.',
        examples=['item'],
    )
    desc: str = Field(
        default='',
        description='A description of the link.',
        examples=['Charmed Kubeflow documentation'],
    )


class RequirerAppData(BaseModel):
    """The requirer's application databag."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'dashboard_links': (
                        '[{"text": "Some link text", "link": "/some-relative-link", "location": "menu",'
                        ' "icon": "assessment", "type": "item", "desc": "link description"},'
                        ' {"text": "Some other link text", "link": "/some-other-relative-link",'
                        ' "location": "quick", "icon": "book", "type": "item", "desc": "link description"}]'
                    ),
                },
                {
                    'dashboard_links': '[]',
                },
            ]
        }
    )

    dashboard_links: Json[list[DashboardItem]] = Field(
        description='The links to show on the dashboard, as a JSON-encoded list.',
        examples=[
            '[{"text": "MLflow", "link": "/mlflow/", "location": "menu", "icon": "icons:link", "type": "item", "desc": ""}]',
        ],
    )


ProviderAppData = None
ProviderUnitData = None
RequirerUnitData = None
