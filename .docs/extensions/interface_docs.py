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

from sphinx.util import logging

logger = logging.getLogger(__name__)

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


def _main(docs_dir: pathlib.Path) -> None:
    """Write automodule file for package and placeholders rst files for all other packages."""
    root = docs_dir.parent
    ref_dir = docs_dir / 'reference' / 'interfaces'
    ref_dir.mkdir(parents=True, exist_ok=True)
    (ref_dir / 'placeholder.md').unlink(missing_ok=True)
    cmd = [root / '.scripts/ls.py', 'interfaces', '--exclude-examples', '--exclude-placeholders']
    interfaces = json.loads(subprocess.check_output(cmd, text=True))
    schema_paths = sorted(
        str(p.relative_to(root))
        for path_str in interfaces
        for p in (root / path_str / 'interface').glob('v[0-9]*/schema.py')
    )
    schemas = _load_schemas(root=root, schema_paths=schema_paths)
    for path_str in interfaces:
        interface_dir = root / path_str
        interface_name = interface_dir.name
        interface_ref_dir = ref_dir / interface_name
        interface_ref_dir.mkdir(exist_ok=True)
        label = f'interfaces-{interface_name.replace("_", "-")}'
        index = INDEX_TEMPLATE.format(label=label, interface_name=interface_name)
        _write_if_needed(path=ref_dir / f'{interface_name}.md', content=index)
        for v in (interface_dir / 'interface').glob('v[0-9]*'):
            readme_raw = (v / 'README.md').read_text()
            schema = schemas.get(str((v / 'schema.py').relative_to(root)))
            if schema is not None:
                readme_raw = add_generated_sections(readme_raw, schema)
            base_url = f'{REPO_MAIN_URL}/interfaces/{interface_name}/interface/{v.name}'
            # match all non-http(s) markdown links and prepend base_url to matching links
            readme = re.sub(
                r'\[(.+)\]\((?!https?://)([^)]+)\)',
                lambda m: f'[{m.group(1)}]({base_url}/{m.group(2)})',  # noqa: B023
                readme_raw,
            )
            content = f'({label}-{v.name})=\n' + readme
            _write_if_needed(path=interface_ref_dir / f'{v.name}.md', content=content)


def _write_if_needed(path: pathlib.Path, content: str) -> None:
    """Write to path only if contents are different.

    This allows sphinx-build to skip rebuilding pages that depend on the output of this extension
    if the output hasn't actually changed.
    """
    if not path.exists() or path.read_text() != content:
        path.write_text(content)


#########################################
# relation data generated from schema.py #
#########################################

DATABAGS = {
    'provider-app': 'Provider application databag',
    'provider-unit': 'Provider unit databag',
    'requirer-app': 'Requirer application databag',
    'requirer-unit': 'Requirer unit databag',
}
_SCHEMA_SCRIPT = pathlib.Path(__file__).parent.parent / 'scripts' / 'interface_schemas.py'

# A JSON Schema, as produced by Pydantic's model_json_schema().
JsonSchema = dict[str, typing.Any]


def _load_schemas(root: pathlib.Path, schema_paths: list[str]) -> dict[str, dict[str, typing.Any]]:
    """Return the databag JSON Schemas for each schema.py, keyed by path relative to root.

    The schemas are imported in a separate environment with the dependencies from
    schema-requirements.txt, so that pydantic isn't needed in the docs environment.
    Schemas that can't be loaded are left out, with a warning.
    """
    if not schema_paths:
        return {}
    cmd = [
        'uv',
        'run',
        '--no-project',
        '--with-requirements',
        str(root / 'schema-requirements.txt'),
        str(_SCHEMA_SCRIPT),
        *schema_paths,
    ]
    try:
        output = subprocess.check_output(cmd, text=True, cwd=root)
    except (OSError, subprocess.CalledProcessError) as e:
        logger.warning(
            'Could not load interface schemas, so relation data is not generated: %s', e
        )
        return {}
    result: dict[str, dict[str, typing.Any]] = {}
    for path, schema in json.loads(output).items():
        if 'error' in schema:
            logger.warning('Could not load interface schema %s:\n%s', path, schema['error'])
            continue
        result[path] = schema['databags']
    return result


def add_generated_sections(readme: str, databags: dict[str, JsonSchema | None]) -> str:
    """Add the relation data tables and the direction diagram generated from the schema.

    The tables go directly under the 'Relation data' heading, or in a new section at the end
    if there isn't one. The diagram goes at the end of the 'Direction' section, or at the
    start of the generated relation data if there isn't one.
    """
    diagram = render_direction_diagram(databags)
    lines = readme.splitlines()
    headings = _level_2_headings(lines)
    direction = headings.get('direction')
    relation_data = render_relation_data(
        databags,
        link_schema='schema.py' not in readme,
        diagram=diagram if direction is None else '',
    )
    relation_data_index = headings.get('relation data')
    if relation_data_index is None:
        lines.extend(['', '## Relation data', '', relation_data])
    else:
        lines[relation_data_index + 1 : relation_data_index + 1] = ['', relation_data]
    if direction is not None and diagram:
        end = _section_end(lines, direction)
        while end > direction + 1 and not lines[end - 1].strip():
            end -= 1
        lines[end:end] = ['', diagram]
    return '\n'.join(lines) + '\n'


def _level_2_headings(lines: list[str]) -> dict[str, int]:
    """Map lowercased '## ' headings outside code fences to their line index."""
    result: dict[str, int] = {}
    for i, line in _lines_outside_fences(lines):
        if line.startswith('## '):
            result.setdefault(line[3:].strip().lower(), i)
    return result


def _section_end(lines: list[str], start: int) -> int:
    """Return the index of the first '# ' or '## ' heading after start, or len(lines)."""
    for i, line in _lines_outside_fences(lines):
        if i > start and (line.startswith('# ') or line.startswith('## ')):
            return i
    return len(lines)


def _lines_outside_fences(lines: list[str]) -> typing.Iterator[tuple[int, str]]:
    fence: str | None = None
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        marker = re.match(r'(`{3,}|~{3,})', stripped)
        if marker:
            if fence is None:
                fence = marker.group(1)
            elif stripped.startswith(fence) and not stripped[len(fence) :].strip():
                fence = None
            continue
        if fence is None:
            yield i, line


def render_direction_diagram(databags: dict[str, JsonSchema | None]) -> str:
    """Return a mermaid diagram of which side writes which fields, or '' if nothing is written."""
    edges: list[str] = []
    for side, other in (('provider', 'requirer'), ('requirer', 'provider')):
        parts: list[str] = []
        for bag in ('app', 'unit'):
            schema = databags.get(f'{side}-{bag}')
            if schema is None:
                continue
            fields = list(schema.get('properties', {}))
            if fields:
                rows = [', '.join(fields[i : i + 3]) for i in range(0, len(fields), 3)]
                parts.append(f'{bag}: ' + ',<br>'.join(rows))
        if parts:
            label = '<br>'.join(parts).replace('"', '#quot;')
            edges.append(f'    {side} -->|"{label}"| {other}')
    if not edges:
        return ''
    return '\n'.join([
        '```mermaid',
        'flowchart LR',
        '    provider[Provider]',
        '    requirer[Requirer]',
        *edges,
        '```',
    ])


def render_relation_data(
    databags: dict[str, JsonSchema | None], link_schema: bool = True, diagram: str = ''
) -> str:
    """Return Markdown with a table per non-empty databag, and one per nested object.

    If diagram is given, it goes before the tables (after the schema link, if any).
    """
    out: list[str] = []
    if link_schema:
        out.extend(['Generated from the [Pydantic schema](schema.py).', ''])
    if diagram:
        out.extend([diagram, ''])
    empty = [title for name, title in DATABAGS.items() if databags.get(name) is None]
    rendered: set[str] = set()
    for name, title in DATABAGS.items():
        schema = databags.get(name)
        if schema is None:
            continue
        defs: dict[str, JsonSchema] = schema.get('$defs', {})
        out.extend([f'### {title}', '', *_fields_table(schema, defs), ''])
        pending = _nested_models(schema, defs)
        while pending:
            model = pending.pop(0)
            if model in rendered:
                continue
            rendered.add(model)
            out.extend([f'#### `{model}`', '', *_fields_table(defs[model], defs), ''])
            pending.extend(_nested_models(defs[model], defs))
    if empty:
        names = [t.removesuffix(' databag').lower() for t in empty]
        out.append(f'Empty databags: {", ".join(names)}.')
    return '\n'.join(out).strip()


def _fields_table(schema: JsonSchema, defs: dict[str, JsonSchema]) -> list[str]:
    properties: dict[str, JsonSchema] = schema.get('properties', {})
    if not properties:
        return ['No fields are defined.']
    required = set(schema.get('required', []))
    rows = ['| Field | Type | Required | Description |', '|---|---|---|---|']
    for field, prop in properties.items():
        if field in required:
            req = 'yes'
        elif 'default' in prop and prop['default'] is not None:
            req = f'no (default `{json.dumps(prop["default"])}`)'
        else:
            req = 'no'
        description = prop.get('description', '')
        if not description and '$ref' in prop:
            description = _resolve(prop, defs).get('description', '')
        rows.append(f'| `{field}` | {_type(prop, defs)} | {req} | {_cell(description)} |')
    return rows


def _type(schema: JsonSchema, defs: dict[str, JsonSchema]) -> str:
    if '$ref' in schema:
        target = _resolve(schema, defs)
        name = schema['$ref'].rsplit('/', 1)[-1]
        if 'enum' in target:
            return _enum(target['enum'])
        if target.get('type') == 'object' and 'properties' in target:
            return f'`{name}` object'
        return _type(target, defs)
    if 'anyOf' in schema or 'oneOf' in schema:
        options: list[JsonSchema] = schema.get('anyOf', schema.get('oneOf', []))
        nullable = any(o.get('type') == 'null' for o in options)
        types = [_type(o, defs) for o in options if o.get('type') != 'null']
        text = ' or '.join(dict.fromkeys(types)) or 'null'
        return f'{text} or null' if nullable and types else text
    if 'allOf' in schema and len(schema['allOf']) == 1:
        return _type(schema['allOf'][0], defs)
    if 'const' in schema:
        return f'`{json.dumps(schema["const"])}`'
    if 'enum' in schema:
        return _enum(schema['enum'])
    if schema.get('contentMediaType') == 'application/json':
        return f'JSON-encoded {_type(schema.get("contentSchema", {}), defs)}'
    type_ = schema.get('type')
    if type_ == 'array':
        items = schema.get('items')
        if not items:
            return 'list'
        item = _type(items, defs)
        if item.startswith('one of '):
            return f'list, each {item}'
        return f'list of {item}s' if item.endswith(' object') else f'list of {item}'
    if type_ == 'object':
        values = schema.get('additionalProperties')
        if isinstance(values, dict) and values:
            return f'mapping of string to {_type(typing.cast("JsonSchema", values), defs)}'
        return 'object'
    if isinstance(type_, str):
        return _with_constraints(type_, schema)
    return 'any'


# Pydantic's JSON Schema format names that don't read well as they are.
_FORMATS = {
    'ipvanyaddress': 'IP address',
    'ipvanyinterface': 'IP interface',
    'ipvanynetwork': 'IP network',
    'uri': 'URI',
    'uuid': 'UUID',
}


def _with_constraints(type_: str, schema: JsonSchema) -> str:
    text = type_
    if 'format' in schema:
        text += f' ({_FORMATS.get(schema["format"], schema["format"])})'
    low = schema.get('minimum', schema.get('exclusiveMinimum'))
    high = schema.get('maximum', schema.get('exclusiveMaximum'))
    if low is not None and high is not None:
        text += f', {low} to {high}'
    elif low is not None:
        text += f', at least {low}'
    elif high is not None:
        text += f', at most {high}'
    if 'minLength' in schema:
        text += f', at least {_characters(schema["minLength"])}'
    if 'maxLength' in schema:
        text += f', at most {_characters(schema["maxLength"])}'
    if 'pattern' in schema:
        text += f', matching `{schema["pattern"]}`'
    return text


def _characters(n: int) -> str:
    return '1 character' if n == 1 else f'{n} characters'


def _enum(values: list[typing.Any]) -> str:
    if len(values) == 1:
        return f'`{json.dumps(values[0]) if not isinstance(values[0], str) else values[0]}`'
    return 'one of ' + ', '.join(
        f'`{json.dumps(v) if not isinstance(v, str) else v}`' for v in values
    )


def _resolve(schema: JsonSchema, defs: dict[str, JsonSchema]) -> JsonSchema:
    return defs.get(schema['$ref'].rsplit('/', 1)[-1], {})


def _nested_models(schema: JsonSchema, defs: dict[str, JsonSchema]) -> list[str]:
    """Return the $defs object models referenced directly by schema's properties, in order."""
    found: list[str] = []

    def walk(node: typing.Any) -> None:
        if isinstance(node, dict):
            node = typing.cast('JsonSchema', node)
            ref = node.get('$ref')
            if isinstance(ref, str):
                name = ref.rsplit('/', 1)[-1]
                target = defs.get(name, {})
                if 'properties' in target and name not in found:
                    found.append(name)
                return
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in typing.cast('list[typing.Any]', node):
                walk(value)

    walk(schema.get('properties', {}))
    return found


def _cell(text: str) -> str:
    """Make text safe for a single Markdown table cell."""
    text = ' '.join(text.split())
    return text.replace('|', '\\|').replace('<', '&lt;')
