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

# ruff: noqa: D103 (function docstrings)

"""Unit tests for the interface preprocessor script."""

from __future__ import annotations

import json
import typing

import interface_preprocessor as ip
import pytest

if typing.TYPE_CHECKING:
    import pathlib

# --- _main ---


def _fake_ls(interfaces: list[str]) -> typing.Callable[..., str]:
    """A stand-in for ``subprocess.check_output`` returning the given interfaces."""

    def check_output(*args: object, **kwargs: object) -> str:
        return json.dumps(interfaces)

    return check_output


def test_main_writes_index_and_version_pages(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """Index stubs and rewritten READMEs are written for each interface."""
    docs_dir = tmp_path / 'docs_site'
    ref_dir = docs_dir / 'reference' / 'interfaces'
    ref_dir.mkdir(parents=True)
    (ref_dir / 'placeholder.md').write_text('# Temporary TOC placeholder')
    v1_dir = tmp_path / 'interfaces' / 'foo' / 'interface' / 'v1'
    v1_dir.mkdir(parents=True)
    (v1_dir / 'README.md').write_text('# Foo v1\n\nSee [schema](schema.md).\n')
    monkeypatch.setattr(ip, '_DOCS_DIR', docs_dir)
    monkeypatch.setattr(ip, '_REPO_ROOT', tmp_path)
    monkeypatch.setattr(ip.subprocess, 'check_output', _fake_ls(['interfaces/foo']))

    ip._main()

    assert not (ref_dir / 'placeholder.md').exists()
    index = (ref_dir / 'foo.md').read_text()
    assert index.startswith('(interfaces-foo)=\n# foo\n')
    assert 'foo/*' in index
    v1 = (ref_dir / 'foo' / 'v1.md').read_text()
    assert v1.startswith('(interfaces-foo-v1)=\n# Foo v1\n')


def test_main_removes_placeholder(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    """The fallback placeholder is removed when the preprocessor runs."""
    docs_dir = tmp_path / 'docs_site'
    ref_dir = docs_dir / 'reference' / 'interfaces'
    ref_dir.mkdir(parents=True)
    (ref_dir / 'placeholder.md').write_text('# Temporary TOC placeholder')
    monkeypatch.setattr(ip, '_DOCS_DIR', docs_dir)
    monkeypatch.setattr(ip, '_REPO_ROOT', tmp_path)
    monkeypatch.setattr(ip.subprocess, 'check_output', _fake_ls([]))

    ip._main()

    assert not (ref_dir / 'placeholder.md').exists()


def test_main_fails_early_on_missing_readme(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """A version directory without a README.md fails before anything is written."""
    docs_dir = tmp_path / 'docs_site'
    ref_dir = docs_dir / 'reference' / 'interfaces'
    ref_dir.mkdir(parents=True)
    (ref_dir / 'placeholder.md').write_text('# Temporary TOC placeholder')
    good = tmp_path / 'interfaces' / 'bar' / 'interface' / 'v0'
    good.mkdir(parents=True)
    (good / 'README.md').write_text('# Bar v0\n')
    for version in ('v0', 'v1'):
        (tmp_path / 'interfaces' / 'foo' / 'interface' / version).mkdir(parents=True)
    monkeypatch.setattr(ip, '_DOCS_DIR', docs_dir)
    monkeypatch.setattr(ip, '_REPO_ROOT', tmp_path)
    interfaces = ['interfaces/bar', 'interfaces/foo']
    monkeypatch.setattr(ip.subprocess, 'check_output', _fake_ls(interfaces))

    with pytest.raises(SystemExit) as exc_info:
        ip._main()

    message = str(exc_info.value.code)
    assert 'README.md' in message
    assert 'interfaces/foo/interface/v0/README.md' in message
    assert 'interfaces/foo/interface/v1/README.md' in message
    assert 'interfaces/bar' not in message
    # Nothing was written, and the placeholder is left for the fallback extension.
    assert sorted(p.name for p in ref_dir.iterdir()) == ['placeholder.md']


def test_main_fails_after_writing_pages_if_there_were_warnings(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """A warning while generating the pages fails the script, once every page is written."""
    docs_dir = tmp_path / 'docs_site'
    ref_dir = docs_dir / 'reference' / 'interfaces'
    ref_dir.mkdir(parents=True)
    v0_dir = tmp_path / 'interfaces' / 'foo' / 'interface' / 'v0'
    v0_dir.mkdir(parents=True)
    (v0_dir / 'README.md').write_text('# Foo v0\n')
    (v0_dir / 'schema.py').write_text('')
    monkeypatch.setattr(ip, '_DOCS_DIR', docs_dir)
    monkeypatch.setattr(ip, '_REPO_ROOT', tmp_path)
    monkeypatch.setattr(ip.subprocess, 'check_output', _fake_ls(['interfaces/foo']))
    monkeypatch.setattr(ip, '_logger', ip._Logger())

    def load_schemas(root: pathlib.Path, schema_paths: list[str]) -> dict[str, typing.Any]:
        assert schema_paths == ['interfaces/foo/interface/v0/schema.py']
        ip._logger.warning('Could not load the interface schemas: %s', 'no uv')
        return {}

    monkeypatch.setattr(ip, '_load_schemas', load_schemas)

    with pytest.raises(SystemExit) as exc_info:
        ip._main()

    assert '1 warning(s)' in str(exc_info.value.code)
    assert (ref_dir / 'foo' / 'v0.md').read_text() == '(interfaces-foo-v0)=\n# Foo v0\n'


# --- _generate_interface_docs ---


def test_generate_index_stub(tmp_path: pathlib.Path):
    """The index stub has a hyphenated label and a glob toctree."""
    interface_dir = tmp_path / 'interfaces' / 'tls_certificates'
    interface_dir.mkdir(parents=True)
    ref_dir = tmp_path / 'ref'
    ref_dir.mkdir()

    ip._generate_interface_docs(interface_dir=interface_dir, ref_dir=ref_dir)

    index = (ref_dir / 'tls_certificates.md').read_text()
    assert index.startswith('(interfaces-tls-certificates)=\n# tls_certificates\n')
    assert 'tls_certificates/*' in index


def test_generate_rewrites_version_readme_links(tmp_path: pathlib.Path):
    """Relative links in version READMEs become absolute GitHub URLs."""
    v2_dir = tmp_path / 'interfaces' / 'foo' / 'interface' / 'v2'
    v2_dir.mkdir(parents=True)
    (v2_dir / 'README.md').write_text(
        '# Foo v2\n\nSee [schema](schema.md) and [docs](https://example.com/).\n'
    )
    ref_dir = tmp_path / 'ref'
    ref_dir.mkdir()

    ip._generate_interface_docs(interface_dir=v2_dir.parent.parent, ref_dir=ref_dir)

    v2 = (ref_dir / 'foo' / 'v2.md').read_text()
    assert v2.startswith('(interfaces-foo-v2)=\n# Foo v2\n')
    base = f'{ip._REPO_MAIN_URL}/interfaces/foo/interface/v2'
    assert f'[schema]({base}/schema.md)' in v2
    assert '[docs](https://example.com/)' in v2


def test_generate_no_interface_dir(tmp_path: pathlib.Path):
    """Interfaces without an interface/ directory get an index stub only."""
    interface_dir = tmp_path / 'interfaces' / 'foo'
    interface_dir.mkdir(parents=True)
    ref_dir = tmp_path / 'ref'
    ref_dir.mkdir()

    ip._generate_interface_docs(interface_dir=interface_dir, ref_dir=ref_dir)

    assert (ref_dir / 'foo.md').exists()
    # The per-interface directory is created, but contains no version pages.
    assert list((ref_dir / 'foo').glob('*.md')) == []


def test_generate_skips_unchanged_files(tmp_path: pathlib.Path):
    """Files whose content hasn't changed are not rewritten."""
    interface_dir = tmp_path / 'interfaces' / 'foo'
    interface_dir.mkdir(parents=True)
    ref_dir = tmp_path / 'ref'
    ref_dir.mkdir()
    index = ref_dir / 'foo.md'

    ip._generate_interface_docs(interface_dir=interface_dir, ref_dir=ref_dir)
    mtime = index.stat().st_mtime_ns

    ip._generate_interface_docs(interface_dir=interface_dir, ref_dir=ref_dir)

    assert index.stat().st_mtime_ns == mtime


# --- _rewrite_links ---


def test_rewrite_links_relative():
    content = 'See [the schema](schema.md) for details.'
    result = ip._rewrite_links(content, 'https://example.com/base')
    assert result == 'See [the schema](https://example.com/base/schema.md) for details.'


def test_rewrite_links_preserves_http():
    content = 'See [docs](https://example.com/page) and [other](http://example.com/).'
    assert ip._rewrite_links(content, 'https://example.com/base') == content


def test_rewrite_links_multiple_relative_on_one_line():
    content = 'See [the schema](schema.py) and [the README](README.md).'
    result = ip._rewrite_links(content, 'https://example.com/base')
    assert result == (
        'See [the schema](https://example.com/base/schema.py)'
        ' and [the README](https://example.com/base/README.md).'
    )


def test_rewrite_links_mixed_on_one_line():
    content = 'See [docs](https://example.com/page), [schema](schema.py), [other](http://x/).'
    result = ip._rewrite_links(content, 'https://example.com/base')
    assert result == (
        'See [docs](https://example.com/page),'
        ' [schema](https://example.com/base/schema.py), [other](http://x/).'
    )


# --- _write_if_needed ---


def test_write_if_needed_writes_missing(tmp_path: pathlib.Path):
    path = tmp_path / 'out.md'
    ip._write_if_needed(path=path, content='content')
    assert path.read_text() == 'content'


def test_write_if_needed_skips_identical(tmp_path: pathlib.Path):
    path = tmp_path / 'out.md'
    path.write_text('content')
    mtime = path.stat().st_mtime_ns
    ip._write_if_needed(path=path, content='content')
    assert path.stat().st_mtime_ns == mtime


def test_write_if_needed_rewrites_different(tmp_path: pathlib.Path):
    path = tmp_path / 'out.md'
    path.write_text('old')
    ip._write_if_needed(path=path, content='new')
    assert path.read_text() == 'new'


# --- library line ---

_LABELS = frozenset({'charmlibs-interfaces-smtp'})
_NEW_SHAPE = '# smtp\n\nThe smtp interface sends mail.\n\n## Direction\n\nOne way.\n'


@pytest.mark.parametrize(
    ('lib', 'expected'),
    [
        (
            'charmlibs.interfaces.smtp',
            'Library: [`charmlibs.interfaces.smtp`](project:#charmlibs-interfaces-smtp)',
        ),
        (
            # A package with no reference page in this repo's docs links to PyPI.
            'charmlibs.interfaces.tls_certificates',
            'Library: [`charmlibs.interfaces.tls_certificates`]'
            '(https://pypi.org/project/charmlibs-interfaces-tls-certificates/)',
        ),
        ('cosl', 'Library: [`cosl`](https://pypi.org/project/cosl/)'),
        # A distribution name and an import name both link to the PyPI project.
        ('litmus-libs', 'Library: [`litmus-libs`](https://pypi.org/project/litmus-libs/)'),
        (
            'dpcharmlibs.interfaces',
            'Library: [`dpcharmlibs.interfaces`](https://pypi.org/project/dpcharmlibs-interfaces/)',
        ),
        (
            'charms.smtp_integrator.smtp',
            'Library: `charms.smtp_integrator.smtp` (Charmhub-hosted)',
        ),
        # Anything else is shown as it is.
        ('charms.smtp', 'Library: `charms.smtp`'),
        ('see the smtp charm', 'Library: `see the smtp charm`'),
    ],
)
def test_render_library_line(lib: str, expected: str):
    line, _ = ip._render_library_line(lib, _LABELS)
    assert line == expected


def test_library_line_goes_at_the_end_of_the_intro():
    result = ip._with_library_line(_NEW_SHAPE, 'charms.smtp_integrator.smtp', _LABELS)
    assert result == (
        '# smtp\n\nThe smtp interface sends mail.\n\n'
        'Library: `charms.smtp_integrator.smtp` (Charmhub-hosted)\n\n'
        '## Direction\n\nOne way.\n'
    )


def test_library_line_without_level_2_headings():
    result = ip._with_library_line('# smtp\n\nSends mail.\n\n', 'cosl', _LABELS)
    assert result == '# smtp\n\nSends mail.\n\nLibrary: [`cosl`](https://pypi.org/project/cosl/)\n'


def test_library_line_ignores_headings_in_code_blocks():
    readme = '# smtp\n\nIntro.\n\n```markdown\n## Usage\n```\n\n## Direction\n'
    result = ip._with_library_line(readme, 'cosl', _LABELS)
    assert result.index('Library: ') > result.index('## Usage')
    assert result.index('Library: ') < result.index('## Direction')


def test_no_library_line_without_lib():
    assert ip._with_library_line(_NEW_SHAPE, None, _LABELS) == _NEW_SHAPE


@pytest.mark.parametrize(
    'readme',
    [
        # The old shape says which library to use in its Usage section, however it's spelled.
        '# `smtp/v0`\n\n## Usage\n\nUse the [smtp library](https://example.com).\n',
        # The new shape names the library in the intro.
        '# smtp\n\nCharms should use [`charmlibs.interfaces.smtp`](https://example.com).\n',
    ],
)
def test_no_library_line_when_the_readme_already_has_one(readme: str):
    assert ip._with_library_line(readme, 'charmlibs.interfaces.smtp', _LABELS) == readme


def test_no_library_line_when_the_readme_links_the_pypi_project():
    readme = '# x\n\nUse [the library](https://pypi.org/project/dpcharmlibs-interfaces/).\n'
    assert ip._with_library_line(readme, 'dpcharmlibs.interfaces', _LABELS) == readme


@pytest.mark.parametrize(
    ('yaml_text', 'expected'),
    [
        ('name: smtp\nlib: charms.smtp_integrator.smtp\n', 'charms.smtp_integrator.smtp'),
        ("name: smtp\nlib: 'cosl'  # quoted, with a comment\n", 'cosl'),
        ('name: smtp\n', None),
        ('name: smtp\nlib:\n', None),
        ('', None),
    ],
)
def test_interface_lib(tmp_path: pathlib.Path, yaml_text: str, expected: str | None):
    (tmp_path / 'interface.yaml').write_text(yaml_text)
    assert ip._interface_lib(tmp_path) == expected


def test_interface_lib_without_interface_yaml(tmp_path: pathlib.Path):
    assert ip._interface_lib(tmp_path) is None


def test_generate_adds_library_line_after_rewriting_links(tmp_path: pathlib.Path):
    v0_dir = tmp_path / 'interfaces' / 'smtp' / 'interface' / 'v0'
    v0_dir.mkdir(parents=True)
    (v0_dir / 'README.md').write_text(_NEW_SHAPE + '\nSee [schema](schema.py).\n')
    (v0_dir / 'interface.yaml').write_text('name: smtp\nlib: charmlibs.interfaces.smtp\n')
    ref_dir = tmp_path / 'ref'
    ref_dir.mkdir()

    ip._generate_interface_docs(
        interface_dir=v0_dir.parent.parent, ref_dir=ref_dir, package_labels=_LABELS
    )

    v0 = (ref_dir / 'smtp' / 'v0.md').read_text()
    assert '[`charmlibs.interfaces.smtp`](project:#charmlibs-interfaces-smtp)' in v0
    assert f'[schema]({ip._REPO_MAIN_URL}/interfaces/smtp/interface/v0/schema.py)' in v0


def test_package_labels(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        ip.subprocess, 'check_output', _fake_ls(['pathops', 'interfaces/tls-certificates'])
    )
    assert ip._package_labels() == {'charmlibs-pathops', 'charmlibs-interfaces-tls-certificates'}
