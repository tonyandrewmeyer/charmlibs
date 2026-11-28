# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for adding and disabling repositories."""

import pathlib
from unittest.mock import patch

import pytest

import charmlibs.apt as apt

EXPECTED_LINE = 'deb [arch=amd64] http://example.com focal main\n'


@pytest.fixture
def repositories(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> apt.RepositoryMapping:
    """An empty :class:`apt.RepositoryMapping` that ignores the system's apt sources."""
    monkeypatch.setattr(apt.RepositoryMapping, '_apt_dir', str(tmp_path))
    return apt.RepositoryMapping()


@pytest.fixture
def repo(tmp_path: pathlib.Path) -> apt.DebianRepository:
    """An enabled repository with an ``arch`` option, writing to a file under ``tmp_path``."""
    return apt.DebianRepository(
        enabled=True,
        repotype='deb',
        uri='http://example.com',
        release='focal',
        groups=['main'],
        filename=str(tmp_path / 'example.com-focal.list'),
        options={'arch': 'amd64'},
    )


@pytest.fixture
def sources_prefix(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Point default repository filenames (``_make_filename``) into ``tmp_path``.

    Returns the ``tmp_path`` repositories are written under.
    """

    def prefix(uri: str) -> str:
        return str(tmp_path / 'example.com')

    monkeypatch.setattr(apt.DebianRepository, 'prefix_from_uri', staticmethod(prefix))
    return tmp_path


def test_add_with_options_writes_source_file_directly(
    repositories: apt.RepositoryMapping,
    repo: apt.DebianRepository,
    tmp_path: pathlib.Path,
) -> None:
    with patch.object(apt.subprocess, 'run') as mock_run:
        repositories.add(repo)

    mock_run.assert_not_called()
    assert (tmp_path / 'example.com-focal.list').read_text() == EXPECTED_LINE
    assert 'deb-http://example.com-focal' in repositories


def test_add_without_options_uses_add_apt_repository(
    repositories: apt.RepositoryMapping,
    tmp_path: pathlib.Path,
) -> None:
    plain_repo = apt.DebianRepository(
        enabled=True,
        repotype='deb',
        uri='http://example.com',
        release='focal',
        groups=['main'],
        filename=str(tmp_path / 'example.com-focal.list'),
    )
    with patch.object(apt.subprocess, 'run') as mock_run:
        repositories.add(plain_repo)

    mock_run.assert_called_once_with(
        [
            'add-apt-repository',
            '--yes',
            '--sourceslist=deb http://example.com focal main',
            '--no-update',
        ],
        check=True,
        capture_output=True,
    )
    assert not (tmp_path / 'example.com-focal.list').exists()


def test_add_with_options_is_idempotent(
    repositories: apt.RepositoryMapping,
    repo: apt.DebianRepository,
    tmp_path: pathlib.Path,
) -> None:
    repositories.add(repo)
    repositories.add(repo)

    assert (tmp_path / 'example.com-focal.list').read_text() == EXPECTED_LINE


def test_add_with_options_then_disable(
    repositories: apt.RepositoryMapping,
    repo: apt.DebianRepository,
    tmp_path: pathlib.Path,
) -> None:
    repositories.add(repo)
    repo.disable()

    assert (tmp_path / 'example.com-focal.list').read_text() == f'# {EXPECTED_LINE}'


def test_add_with_options_and_gpg_key_then_disable(
    repositories: apt.RepositoryMapping,
    tmp_path: pathlib.Path,
) -> None:
    key_file = tmp_path / 'test.gpg'
    key_file.write_bytes(b'')
    repo = apt.DebianRepository(
        enabled=True,
        repotype='deb',
        uri='http://example.com',
        release='focal',
        groups=['main'],
        filename=str(tmp_path / 'example.com-focal.list'),
        gpg_key_filename=str(key_file),
        options={'arch': 'amd64'},
    )
    repositories.add(repo)

    # the line must include signed-by, or disable() cannot find it to comment out
    assert (tmp_path / 'example.com-focal.list').read_text() == (
        f'deb [arch=amd64 signed-by={key_file}] http://example.com focal main\n'
    )

    repo.disable()
    assert (tmp_path / 'example.com-focal.list').read_text() == (
        f'# deb [arch=amd64 signed-by={key_file}] http://example.com focal main\n'
    )


def test_add_with_options_without_filename_writes_default_file(
    repositories: apt.RepositoryMapping,
    sources_prefix: pathlib.Path,
) -> None:
    repo = apt.DebianRepository(
        enabled=True,
        repotype='deb',
        uri='http://example.com',
        release='focal',
        groups=['main'],
        options={'arch': 'amd64'},
    )
    repositories.add(repo)

    assert repo.filename == str(sources_prefix / 'example.com-focal.list')
    assert (sources_prefix / 'example.com-focal.list').read_text() == EXPECTED_LINE


def test_from_repo_line_with_options_writes_file_directly(
    sources_prefix: pathlib.Path,
) -> None:
    with patch.object(apt.subprocess, 'run') as mock_run:
        repo = apt.DebianRepository.from_repo_line(
            'deb [arch=amd64] http://example.com focal main'
        )

    mock_run.assert_not_called()
    assert repo.options == {'arch': 'amd64'}
    assert (sources_prefix / 'example.com-focal.list').read_text() == EXPECTED_LINE


def test_add_disabled_repo_does_nothing(
    repositories: apt.RepositoryMapping,
    tmp_path: pathlib.Path,
) -> None:
    repo = apt.DebianRepository(
        enabled=False,
        repotype='deb',
        uri='http://example.com',
        release='focal',
        groups=['main'],
        filename=str(tmp_path / 'example.com-focal.list'),
        options={'arch': 'amd64'},
    )
    with patch.object(apt.subprocess, 'run') as mock_run:
        repositories.add(repo)

    mock_run.assert_not_called()
    assert not (tmp_path / 'example.com-focal.list').exists()
    assert 'deb-http://example.com-focal' not in repositories


def test_add_repository_with_options_and_update_cache(
    repo: apt.DebianRepository,
) -> None:
    with patch.object(apt.subprocess, 'run') as mock_run:
        apt._add_repository(repo, update_cache=True)

    mock_run.assert_called_once_with(
        ['apt-get', 'update', '--error-on=any'],
        capture_output=True,
        check=True,
    )
