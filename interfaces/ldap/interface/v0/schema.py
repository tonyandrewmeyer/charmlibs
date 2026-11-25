# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""LDAP relation schema definitions."""

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, Json


class ProviderAppData(BaseModel):
    """LDAP provider relation data schema."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'urls': '["ldap://ldap.canonical.com:3893", "ldap://ldap.ubuntu.com:3893"]',
                    'ldaps_urls': '["ldaps://ldap.canonical.com:3894", "ldaps://ldap.ubuntu.com:3894"]',
                    'base_dn': 'dc=canonical,dc=com',
                    'bind_dn': 'cn=sssd,ou=mymodel,dc=canonical,dc=com',
                    'bind_password_secret': 'secret:cjqub6vubg2s77p3nio0',
                    'auth_method': 'simple',
                    'starttls': 'True',
                },
                {
                    'urls': '["ldap://glauth-k8s.mymodel.svc.cluster.local:3893"]',
                    'ldaps_urls': '[]',
                    'base_dn': 'dc=glauth,dc=com',
                    'starttls': 'False',
                },
            ]
        }
    )

    urls: Json[list[AnyUrl]] = Field(
        description='The LDAP URLs of the server, as a JSON list.',
        title='LDAP URLs',
        examples=['["ldap://ldap.canonical.com:3893", "ldap://ldap.ubuntu.com:3893"]'],
    )
    ldaps_urls: Json[list[AnyUrl]] | None = Field(
        default=None,
        description='The LDAPS URLs of the server, as a JSON list, which is empty without LDAPS.',
        title='LDAPS URLs',
        examples=['["ldaps://ldap.canonical.com:3894", "ldaps://ldap.ubuntu.com:3894"]', '[]'],
    )
    base_dn: str = Field(
        description='The base entry, as the starting point for LDAP search operations.',
        title='Base DN',
        examples=['dc=canonical,dc=com'],
    )
    bind_dn: str | None = Field(
        default=None,
        description='The distinguished name (DN) of the bind account for the requirer.',
        title='Bind DN',
        examples=['cn=sssd,ou=mymodel,dc=canonical,dc=com'],
    )
    bind_password_secret: str | None = Field(
        default=None,
        description=(
            "The ID of the Juju secret that holds the bind account's password, "
            'under the `password` key.'
        ),
        title='Bind password secret',
        examples=['secret:cjqub6vubg2s77p3nio0'],
    )
    auth_method: str | None = Field(
        default=None,
        description='The LDAP authentication method.',
        title='Authentication method',
        examples=['simple'],
    )
    starttls: bool = Field(
        description='Whether the server supports StartTLS. Written as `True` or `False`.',
        title='StartTLS',
        examples=['True', 'False'],
    )


class RequirerAppData(BaseModel):
    """LDAP requirer relation data schema."""

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {'user': 'sssd', 'group': 'machine-localhost'},
                {'user': 'postgresql', 'group': 'mymodel'},
            ]
        }
    )

    user: str | None = Field(
        default=None,
        description='The user name for the bind account. Defaults to the application name.',
        examples=['sssd'],
    )
    group: str | None = Field(
        default=None,
        description='The group name for the bind account. Defaults to the model name.',
        examples=['machine-localhost', 'mymodel'],
    )


ProviderUnitData = None
RequirerUnitData = None
