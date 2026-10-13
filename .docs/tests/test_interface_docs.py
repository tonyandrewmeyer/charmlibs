# Copyright 2026 Canonical Ltd.
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

# ruff: noqa: D103 (function docstrings)

"""Unit tests for generating schema tables in the 'interface_docs' local Sphinx extension."""

from __future__ import annotations

import json
import typing

import interface_docs

if typing.TYPE_CHECKING:
    import pathlib

SCHEMA = {
    'required': ['jobs'],
    'properties': {
        'jobs': {
            'type': 'array',
            'description': 'The jobs.',
            'items': {
                'required': ['job-id'],
                'properties': {
                    'job-id': {'type': 'string', 'description': 'An id | with a pipe.'},
                    'status': {'type': ['string', 'null'], 'title': 'Status'},
                },
            },
        },
    },
}


def test_schema_table():
    assert interface_docs._schema_table(SCHEMA).splitlines() == [
        '| Field | Type | Required | Description |',
        '| --- | --- | --- | --- |',
        '| `jobs` | array | yes | The jobs. |',
        '| `jobs[].job-id` | string | yes | An id \\| with a pipe. |',
        '| `jobs[].status` | string | null | no | Status |',
    ]


def test_expand_schema_tables(tmp_path: pathlib.Path):
    (tmp_path / 'schemas').mkdir()
    (tmp_path / 'schemas' / 'provider.json').write_text(json.dumps(SCHEMA))
    readme = 'Before\n<!-- schema-table: schemas/provider.json -->\nAfter\n'
    result = interface_docs._expand_schema_tables(readme, tmp_path)
    assert result.startswith('Before\n| Field |')
    assert result.endswith('|\nAfter\n')


def test_expand_schema_tables_without_marker(tmp_path: pathlib.Path):
    assert interface_docs._expand_schema_tables('# Hello\n', tmp_path) == '# Hello\n'
