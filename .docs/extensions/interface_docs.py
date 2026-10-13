# Copyright 2025 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Include interface reference docs in docs site."""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import typing

####################
# Sphinx extension #
####################

if typing.TYPE_CHECKING:
    import sphinx.application


def setup(app: sphinx.application.Sphinx) -> dict[str, str | bool]:
    """Entrypoint for Sphinx extensions, connects generation code to Sphinx event."""
    app.connect('builder-inited', _interface_docs)
    return {'version': '1.0.0', 'parallel_read_safe': False, 'parallel_write_safe': False}


def _interface_docs(app: sphinx.application.Sphinx) -> None:
    if app.config.package is not None:
        # For efficiency, don't write interface docs during the package reference docs passes.
        # But we need to make sure something is there so that the TOC glob doesn't fail.
        ref_dir = pathlib.Path(app.confdir, 'reference', 'interfaces')
        ref_dir.mkdir(parents=True, exist_ok=True)
        _write_if_needed(path=ref_dir / 'placeholder.md', content='# Temporary TOC placeholder')
        return
    _main(docs_dir=pathlib.Path(app.confdir))


####################
# generation logic #
####################

INDEX_TEMPLATE = """
({label})=
# {interface_name}

```{{toctree}}
:glob:
:reversed:
:maxdepth: 1

{interface_name}/*
```
""".strip()
REPO_MAIN_URL = 'https://github.com/canonical/charmlibs/blob/main'
# A README can contain `<!-- schema-table: schemas/provider.json -->` to have the field table for
# that schema generated at docs build time, so that the schema is the only source of truth.
SCHEMA_TABLE_MARKER = re.compile(r'<!--\s*schema-table:\s*(\S+?)\s*-->')


def _main(docs_dir: pathlib.Path) -> None:
    """Write automodule file for package and placeholders rst files for all other packages."""
    root = docs_dir.parent
    ref_dir = docs_dir / 'reference' / 'interfaces'
    ref_dir.mkdir(parents=True, exist_ok=True)
    (ref_dir / 'placeholder.md').unlink(missing_ok=True)
    cmd = [root / '.scripts/ls.py', 'interfaces', '--exclude-examples', '--exclude-placeholders']
    interfaces = json.loads(subprocess.check_output(cmd, text=True))
    for path_str in interfaces:
        interface_dir = root / path_str
        interface_name = interface_dir.name
        interface_ref_dir = ref_dir / interface_name
        interface_ref_dir.mkdir(exist_ok=True)
        label = f'interfaces-{interface_name.replace("_", "-")}'
        index = INDEX_TEMPLATE.format(label=label, interface_name=interface_name)
        _write_if_needed(path=ref_dir / f'{interface_name}.md', content=index)
        for v in (interface_dir / 'interface').glob('v[0-9]*'):
            readme_raw = _expand_schema_tables((v / 'README.md').read_text(), v)
            base_url = f'{REPO_MAIN_URL}/interfaces/{interface_name}/interface/{v.name}'
            # match all non-http(s) markdown links and prepend base_url to matching links
            readme = re.sub(
                r'\[(.+)\]\((?!https?://)([^)]+)\)',
                lambda m: f'[{m.group(1)}]({base_url}/{m.group(2)})',  # noqa: B023
                readme_raw,
            )
            content = f'({label}-{v.name})=\n' + readme
            _write_if_needed(path=interface_ref_dir / f'{v.name}.md', content=content)


def _expand_schema_tables(readme: str, version_dir: pathlib.Path) -> str:
    """Replace each schema-table marker in the README with a table generated from the schema."""

    def replace(match: re.Match[str]) -> str:
        schema = json.loads((version_dir / match.group(1)).read_text())
        return _schema_table(schema)

    return SCHEMA_TABLE_MARKER.sub(replace, readme)


def _schema_table(schema: dict[str, typing.Any]) -> str:
    """Render the fields of a JSON schema as a Markdown table.

    Nested object properties and array items are flattened using dotted paths, with `[]` marking
    array items.
    """
    rows = ['| Field | Type | Required | Description |', '| --- | --- | --- | --- |']
    rows.extend(_schema_rows(schema, prefix=''))
    return '\n'.join(rows)


def _schema_rows(schema: dict[str, typing.Any], prefix: str) -> list[str]:
    rows: list[str] = []
    required = set(schema.get('required', []))
    for name, prop in schema.get('properties', {}).items():
        path = f'{prefix}{name}'
        type_ = prop.get('type', '')
        if isinstance(type_, list):
            type_ = ' | '.join(type_)
        description = prop.get('description') or prop.get('title') or ''
        description = ' '.join(description.split()).replace('|', '\\|')
        is_required = 'yes' if name in required else 'no'
        rows.append(f'| `{path}` | {type_} | {is_required} | {description} |')
        if prop.get('type') == 'array' and isinstance(prop.get('items'), dict):
            rows.extend(_schema_rows(prop['items'], prefix=f'{path}[].'))
        else:
            rows.extend(_schema_rows(prop, prefix=f'{path}.'))
    return rows


def _write_if_needed(path: pathlib.Path, content: str) -> None:
    """Write to path only if contents are different.

    This allows sphinx-build to skip rebuilding pages that depend on the output of this extension
    if the output hasn't actually changed.
    """
    if not path.exists() or path.read_text() != content:
        path.write_text(content)
