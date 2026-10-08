# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

# pyright: reportPrivateUsage=false

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import pytest

from charmlibs import snap
from charmlibs.snap import _client
from charmlibs.snap_testing import Snap, Snapd, mocked
from charmlibs.snap_testing import _state as state

if TYPE_CHECKING:
    from collections.abc import Callable


class TestJoining:
    def test_joins_an_open_snapd(self):
        snapd = Snapd([Snap('prometheus', channel='2/stable')])
        with snapd:
            with mocked() as joined:
                assert joined is snapd
                snap.refresh('prometheus', '2/edge')
            with mocked():
                snap.install('grafana')
            assert _client.post == snapd._api.post
        assert set(snapd.installed) == {'prometheus', 'grafana'}
        assert snapd.installed['prometheus'].channel == '2/edge'

    def test_joins_the_innermost_open_snapd(self):
        with Snapd(), Snapd() as inner, mocked() as joined:
            assert joined is inner

    def test_joined_snapd_stays_strict(self):
        with Snapd(), mocked():
            with pytest.raises(snap.NotInstalledError):
                snap.list_one('prometheus')


class TestWithoutSnapd:
    def test_patches_the_client_and_puts_it_back(self):
        original = _client.post
        with mocked():
            assert _client.post is not original
        assert _client.post is original

    def test_yields_a_snapd_with_nothing_to_report(self):
        with mocked() as snapd:
            assert isinstance(snapd, Snapd)
            snap.install('prometheus')
            snap.set('prometheus', {'port': 9090})
            snap.connect(('prometheus', 'network'), ('core', 'network'))
            assert snapd.installed == {}
            assert snapd.connections == frozenset()
            assert snapd.history == []

    def test_nested_mocked_joins_the_outer_one(self):
        with mocked() as outer:
            with mocked() as inner:
                assert inner is outer
                snap.install('prometheus')
            assert outer.installed == {}
            assert snap.list_one('grafana').tracking == 'latest/stable'

    def test_snapd_opened_inside_takes_over_until_it_closes(self):
        with mocked() as outer:
            stateless_post = _client.post
            with Snapd([Snap('grafana')]) as snapd:
                with pytest.raises(snap.NotInstalledError):
                    snap.list_one('prometheus')
                with mocked() as joined:
                    assert joined is snapd
                    snap.install('prometheus')
            assert _client.post == stateless_post
            assert snap.list_one('loki').tracking == 'latest/stable'
            assert outer.installed == {}
        assert set(snapd.installed) == {'grafana', 'prometheus'}
        assert snapd.history == [
            state.Install(snap='prometheus', channel=None, revision=None, classic=False)
        ]

    def test_separate_scopes_are_separate_objects(self):
        with mocked() as first:
            pass
        with mocked() as second:
            assert second is not first


class TestSnaps:
    def test_every_snap_is_installed_with_the_defaults(self):
        with mocked():
            info = snap.list_one('prometheus')
        assert info.name == 'prometheus'
        assert info.tracking == 'latest/stable'
        assert info.revision == '1'
        assert info.version == '1.0'
        assert not info.classic
        assert info.hold is None

    def test_install_succeeds_every_time(self):
        with mocked():
            assert snap.install('prometheus')
            assert snap.install('prometheus', '2/stable', revision=7, classic=True)

    def test_refresh_succeeds(self):
        with mocked():
            assert snap.refresh('prometheus')
            assert snap.refresh('prometheus', '2/edge', revision=7)

    def test_remove_succeeds_every_time(self):
        with mocked():
            assert snap.remove('prometheus')
            assert snap.remove('prometheus', purge=True)

    def test_refresh_doesnt_change_what_list_one_reports(self):
        with mocked():
            snap.refresh('prometheus', '2/edge', revision=7)
            info = snap.list_one('prometheus')
        assert (info.tracking, info.revision) == ('latest/stable', '1')

    def test_hold_and_unhold(self):
        with mocked():
            snap.hold('prometheus')
            snap.hold('prometheus', 60)
            assert snap.list_one('prometheus').hold is None
            snap.unhold('prometheus')

    @pytest.mark.parametrize(
        ('kwargs', 'expected'),
        [
            ({}, True),
            ({'update': False}, False),
            ({'channel': 'latest/stable', 'update': False}, False),
            ({'channel': '2/stable'}, True),
            ({'channel': 'edge'}, True),
            ({'revision': 1}, False),
            ({'revision': '1', 'channel': 'stable'}, False),
            ({'revision': 7}, True),
        ],
    )
    def test_ensure_installed(self, kwargs: dict[str, Any], expected: bool):
        with mocked():
            assert bool(snap.ensure_installed('prometheus', **kwargs)) is expected


class TestConfig:
    @pytest.mark.parametrize('name', ['grafana', 'system', 'core'])
    def test_reads_see_no_configuration(self, name: str):
        with mocked():
            assert snap.get(name) == {}
            assert snap.get(name, []) == {}
            with pytest.raises(snap.OptionNotFoundError):
                snap.get(name, 'http.port')
            with pytest.raises(snap.OptionNotFoundError):
                snap.get_one(name, 'http.port')

    def test_a_key_just_set_still_isnt_found(self):
        with mocked():
            snap.set('grafana', {'http.port': 3000})
            with pytest.raises(snap.OptionNotFoundError):
                snap.get_one('grafana', 'http.port')
            assert snap.get('grafana') == {}

    def test_set_and_unset_succeed(self):
        with mocked():
            snap.set('grafana', {'http.port': 3000, 'old': None})
            snap.set('system', {'some.option': 'x'})
            snap.unset('grafana', ['http.port', 'never.set'])

    def test_ensure_vitality_hint_always_adds(self):
        with mocked():
            assert snap.ensure_vitality_hint('prometheus')
            assert snap.ensure_vitality_hint('prometheus')

    def test_ensure_vitality_hint_accepts_what_snapd_would_reject(self):
        # The snap name is snapd's to check, not the library's.
        with mocked():
            assert snap.ensure_vitality_hint('Not-A-Snap-Name')


class TestServices:
    @pytest.mark.parametrize('services', [None, 'prometheus', ['prometheus', 'other'], []])
    def test_start_stop_restart(self, services: str | list[str] | None):
        with mocked():
            snap.start('prometheus', services, enable=True)
            snap.stop('prometheus', services, disable=True)
            snap.restart('prometheus', services)

    def test_logs_are_empty(self):
        with mocked():
            assert snap.logs() == []
            assert snap.logs('prometheus') == []
            assert snap.logs(['prometheus', 'grafana'], limit=None) == []


class TestInterfacesAndAliases:
    def test_connect_and_disconnect(self):
        plug = ('telegraf', 'system-observe')
        slot = ('core', 'system-observe')
        with mocked():
            snap.connect(plug, slot)
            snap.connect(plug)
            snap.connect(plug, 'other')
            snap.disconnect(plug, slot)
            snap.disconnect(plug, slot)
            snap.disconnect(plug)
            snap.disconnect(slot=slot, forget=True)

    def test_alias_and_unalias(self):
        with mocked():
            snap.alias('prometheus', 'promtool', 'promtool')
            snap.unalias('promtool')
            snap.unalias('never-created')


class TestSystemInfo:
    def test_reports_the_default_architecture(self):
        with mocked():
            assert snap.system_info().architecture == 'amd64'


class TestLibraryValidationStillRuns:
    def test_invalid_snap_name(self):
        with mocked():
            with pytest.raises(ValueError):
                snap.install('')
            with pytest.raises(ValueError):
                snap.list_one('foo/bar')
            with pytest.raises(ValueError):
                snap.ensure_installed(' ')

    def test_revision_is_keyword_only(self):
        with mocked():
            with pytest.raises(TypeError):
                snap.install('foo', '2/stable', 7)  # pyright: ignore[reportCallIssue]

    def test_other_argument_checks(self):
        with mocked():
            with pytest.raises(ValueError):
                snap.ensure_vitality_hint('snapd')
            with pytest.raises(ValueError):
                snap.logs('prometheus', limit=0)
            with pytest.raises(ValueError):
                snap.get('grafana', 'a,b')
            with pytest.raises(ValueError):
                snap.set('grafana', {' ': 1})
            with pytest.raises(ValueError):
                snap.alias('prometheus', '', 'promtool')
            with pytest.raises(ValueError):
                snap.connect(('telegraf', ' '))


class TestUnmodelled:
    @pytest.mark.parametrize(
        ('method', 'args'),
        [
            ('get', ('/v2/snapshots',)),
            ('post', ('/v2/snapshots', {'action': 'create'})),
            ('put', ('/v2/snaps/grafana',)),
            ('post', ('/v2/snaps/grafana', {'action': 'switch'})),
            ('post', ('/v2/apps', {'action': 'enable'})),
            ('post', ('/v2/interfaces', {'action': 'auto-connect'})),
            ('post', ('/v2/aliases', {'action': 'prefer'})),
        ],
    )
    def test_raises_not_implemented(self, method: str, args: tuple[Any, ...]):
        with mocked():
            with pytest.raises(NotImplementedError):
                getattr(_client, method)(*args)


def _operations() -> list[Callable[[], object]]:
    """A charm's worth of calls whose results don't depend on how mocked() is opened."""
    return [
        lambda: snap.ensure_installed('prometheus', '2/stable'),
        lambda: snap.list_one('prometheus'),
        lambda: snap.ensure_installed('prometheus', '2/stable'),
        lambda: snap.install('grafana'),
        lambda: snap.install('grafana'),
        lambda: snap.set('grafana', {'http.port': 3000}),
        lambda: snap.get('grafana'),
        lambda: snap.get_one('grafana', 'http.port'),
        lambda: snap.hold('prometheus'),
        lambda: snap.list_one('prometheus').hold,
        lambda: snap.start('prometheus', 'prometheus'),
        lambda: snap.logs('prometheus'),
        lambda: snap.connect(('telegraf', 'system-observe')),
        lambda: snap.disconnect(('telegraf', 'system-observe'), ('core', 'system-observe')),
        lambda: snap.alias('prometheus', 'promtool', 'promtool'),
        lambda: snap.unalias('promtool'),
        lambda: snap.ensure_vitality_hint('prometheus'),
        lambda: snap.ensure_vitality_hint('prometheus'),
        lambda: snap.remove('grafana'),
        lambda: snap.remove('grafana'),
        lambda: snap.system_info(),
    ]


def _outcome(operation: Callable[[], object]) -> object:
    try:
        return repr(operation())
    except snap.Error as e:
        return type(e)


class TestScopeMakesNoDifference:
    def test_once_per_operation_or_once_for_all(self):
        with mocked():
            once = [_outcome(op) for op in _operations()]
        per_operation: list[object] = []
        for op in _operations():
            with mocked():
                per_operation.append(_outcome(op))
        assert per_operation == once

    def test_nested_scopes_give_the_same_results(self):
        with mocked():
            flat = [_outcome(op) for op in _operations()]
        nested: list[object] = []
        with mocked():
            for i, op in enumerate(_operations()):
                with mocked() if i % 2 else contextlib.nullcontext():
                    nested.append(_outcome(op))
        assert nested == flat
