# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

# pyright: reportPrivateUsage=false

from __future__ import annotations

import datetime

import pytest

from charmlibs import snap
from charmlibs.snap import _client
from charmlibs.snap._errors import (
    AppNotFoundError,
    ChannelNotAvailableError,
    NeedsClassicError,
    NotFoundError,
    NotInstalledError,
    OptionNotFoundError,
    _InterfacesUnchangedError,
)
from charmlibs.snap_testing import (
    Connection,
    Failure,
    Snap,
    Snapd,
    SnapStateValidationError,
    StoreSnap,
)
from charmlibs.snap_testing import _state as state


class TestInstallPermissive:
    def test_synthesised_fields(self):
        with Snapd() as snapd:
            assert snap.install('prometheus') is True
        assert snapd.installed == {'prometheus': Snap('prometheus')}
        assert snapd.history == [
            state.Install(snap='prometheus', channel=None, revision=None, classic=False)
        ]

    def test_channel_and_classic(self):
        with Snapd() as snapd:
            snap.install('prometheus', channel='2/edge', classic=True)
        installed = snapd.installed['prometheus']
        assert installed.channel == '2/edge'
        assert installed.classic is True

    def test_revision(self):
        with Snapd() as snapd:
            snap.install('prometheus', revision=7)
        assert snapd.installed['prometheus'].revision == '7'

    def test_already_installed_returns_false_and_is_not_recorded_twice(self):
        with Snapd([Snap('prometheus')]) as snapd:
            assert snap.install('prometheus') is False
        assert snapd.history == []


class TestInstallAuthoritative:
    def test_snap_not_in_store_raises(self):
        with Snapd(store=[StoreSnap('grafana')]):
            with pytest.raises(NotFoundError):
                snap.install('prometheus')

    def test_channel_not_on_store_snap_raises(self):
        store_snap = StoreSnap('grafana', channels={'latest/stable': 1})
        with Snapd(store=[store_snap]):
            with pytest.raises(ChannelNotAvailableError):
                snap.install('grafana', channel='2/edge')

    def test_needs_classic(self):
        store_snap = StoreSnap('grafana', classic=True)
        with Snapd(store=[store_snap]):
            with pytest.raises(NeedsClassicError):
                snap.install('grafana')
            snap.install('grafana', classic=True)  # Succeeds with classic=True.

    def test_fields_synthesised_from_store_snap(self):
        store_snap = StoreSnap(
            'grafana',
            channels={'latest/stable': 100},
            version='9.9',
            services=['grafana'],
            daemon_services=['grafana'],
        )
        with Snapd(store=[store_snap]) as snapd:
            snap.install('grafana')
        assert snapd.installed['grafana'] == Snap(
            'grafana', revision='100', version='9.9', services={'grafana': 'active'}
        )


class TestRefresh:
    def test_permissive_keeps_seeded_revision_unless_named(self):
        with Snapd([Snap('prometheus', channel='2/stable', revision='100')]) as snapd:
            assert snap.refresh('prometheus') is True
        assert snapd.installed['prometheus'].revision == '100'

    def test_permissive_named_revision_moves(self):
        with Snapd([Snap('prometheus', revision='100')]) as snapd:
            snap.refresh('prometheus', revision=101)
        assert snapd.installed['prometheus'].revision == '101'

    def test_permissive_channel_moves(self):
        with Snapd([Snap('prometheus', channel='2/stable')]) as snapd:
            snap.refresh('prometheus', channel='2/edge')
        assert snapd.installed['prometheus'].channel == '2/edge'

    def test_not_installed_raises_not_installed_error(self):
        with Snapd():
            with pytest.raises(NotInstalledError):
                snap.refresh('prometheus')

    def test_authoritative_no_update_available(self):
        store_snap = StoreSnap('prometheus', channels={'latest/stable': 100})
        with Snapd([Snap('prometheus', revision='100')], store=[store_snap]):
            assert snap.refresh('prometheus') is False

    def test_authoritative_update_available(self):
        store_snap = StoreSnap('prometheus', channels={'latest/stable': 101})
        with Snapd([Snap('prometheus', revision='100')], store=[store_snap]) as snapd:
            assert snap.refresh('prometheus') is True
        assert snapd.installed['prometheus'].revision == '101'


class TestEnsure:
    def test_installs_when_missing(self):
        with Snapd() as snapd:
            assert snap.ensure('prometheus', channel='2/stable') is True
        assert snapd.installed['prometheus'].channel == '2/stable'
        assert snapd.history == [
            state.Install(snap='prometheus', channel='2/stable', revision=None, classic=False)
        ]

    def test_refreshes_on_channel_change(self):
        with Snapd([Snap('prometheus', channel='2/stable')]) as snapd:
            assert snap.ensure('prometheus', channel='2/edge') is True
        assert snapd.installed['prometheus'].channel == '2/edge'
        assert isinstance(snapd.history[0], state.Refresh)

    def test_update_false_skips_refresh(self):
        with Snapd([Snap('prometheus', channel='2/stable')]) as snapd:
            assert snap.ensure('prometheus', channel='2/stable', update=False) is False
        assert snapd.history == []


class TestRemove:
    def test_removes_installed(self):
        with Snapd([Snap('prometheus')]) as snapd:
            assert snap.remove('prometheus') is True
        assert snapd.installed == {}
        assert snapd.history == [state.Remove(snap='prometheus', purge=False)]

    def test_not_installed_returns_false(self):
        with Snapd():
            assert snap.remove('prometheus') is False

    def test_purge(self):
        with Snapd([Snap('prometheus')]) as snapd:
            snap.remove('prometheus', purge=True)
        assert snapd.history == [state.Remove(snap='prometheus', purge=True)]


class TestHoldUnhold:
    def test_hold_forever_by_default(self):
        with Snapd([Snap('prometheus')]) as snapd:
            snap.hold('prometheus')
        assert snapd.installed['prometheus'].hold == datetime.datetime.max
        assert snapd.history == [state.Hold(snap='prometheus', until=None)]

    def test_hold_duration(self):
        before = datetime.datetime.now(datetime.timezone.utc)
        with Snapd([Snap('prometheus')]) as snapd:
            snap.hold('prometheus', duration=datetime.timedelta(days=2))
        hold = snapd.installed['prometheus'].hold
        assert hold is not None
        assert hold > before + datetime.timedelta(days=1)

    def test_hold_not_installed_raises(self):
        with Snapd():
            with pytest.raises(NotFoundError):
                snap.hold('prometheus')

    def test_unhold(self):
        with Snapd([Snap('prometheus', hold=datetime.datetime.max)]) as snapd:
            snap.unhold('prometheus')
        assert snapd.installed['prometheus'].hold is None


class TestServices:
    def test_start_all_services(self):
        seeded = Snap('prometheus', services={'prometheus': 'inactive', 'exporter': 'inactive'})
        with Snapd([seeded]) as snapd:
            snap.start('prometheus')
        assert snapd.installed['prometheus'].services == {
            'prometheus': 'active',
            'exporter': 'active',
        }
        assert snapd.history == [
            state.Start(snap='prometheus', services=('prometheus', 'exporter'), enable=False)
        ]

    def test_start_named_service_and_enable(self):
        seeded = Snap('prometheus', services={'prometheus': 'inactive', 'exporter': 'inactive'})
        with Snapd([seeded]) as snapd:
            snap.start('prometheus', 'exporter', enable=True)
        assert snapd.installed['prometheus'].services['exporter'] == 'active'
        assert snapd.installed['prometheus'].services['prometheus'] == 'inactive'
        assert snapd.history == [
            state.Start(snap='prometheus', services=('exporter',), enable=True)
        ]

    def test_start_missing_service_raises(self):
        with Snapd([Snap('prometheus', services={'prometheus': 'inactive'})]):
            with pytest.raises(AppNotFoundError):
                snap.start('prometheus', 'nope')

    def test_start_missing_snap_raises(self):
        with Snapd():
            with pytest.raises(AppNotFoundError):
                snap.start('prometheus')

    def test_stop_disable(self):
        seeded = Snap('prometheus', services={'prometheus': 'active'})
        with Snapd([seeded]) as snapd:
            snap.stop('prometheus', disable=True)
        assert snapd.installed['prometheus'].services['prometheus'] == 'inactive'
        assert snapd.history == [
            state.Stop(snap='prometheus', services=('prometheus',), disable=True)
        ]

    def test_restart(self):
        seeded = Snap('prometheus', services={'prometheus': 'active'})
        with Snapd([seeded]) as snapd:
            snap.restart('prometheus')
        assert snapd.history == [state.Restart(snap='prometheus', services=('prometheus',))]


class TestLogs:
    def _entry(self, message: str, minute: int = 0) -> snap.LogEntry:
        return snap.LogEntry(
            timestamp=datetime.datetime(2026, 1, 1, 0, minute, tzinfo=datetime.timezone.utc),
            sid='prometheus',
            pid=42,
            message=message,
        )

    def test_returns_seeded_entries_verbatim(self):
        entries = [self._entry('one'), self._entry('two', minute=1)]
        with Snapd([Snap('prometheus', logs=entries)]):
            result = snap.logs('prometheus')
        assert [e.message for e in result] == ['one', 'two']
        assert result[0].timestamp == entries[0].timestamp
        assert result[0].pid == 42
        assert result[0].sid == 'prometheus'

    def test_no_limit_filtering(self):
        entries = [self._entry(str(i), minute=i) for i in range(12)]
        with Snapd([Snap('prometheus', logs=entries)]):
            result = snap.logs('prometheus')  # default limit=10
        assert len(result) == 12  # Not sliced to 10: section 10 says logs is canned only.

    def test_missing_snap_raises_not_found(self):
        with Snapd():
            with pytest.raises(NotFoundError):
                snap.logs('prometheus')

    def test_no_names_returns_all_installed(self):
        a = Snap('a', logs=[self._entry('from-a')])
        b = Snap('b', logs=[self._entry('from-b')])
        with Snapd([a, b]):
            result = snap.logs()
        assert {e.message for e in result} == {'from-a', 'from-b'}


class TestFailureInjection:
    def test_wildcard_simulates_snapd_down(self):
        error = snap.ConnectionError(
            'Could not connect to snapd', kind='charmlibs-snap-socket-not-found', value=''
        )
        with Snapd(failures=[Failure('*', error=error)]) as snapd:
            with pytest.raises(snap.ConnectionError):
                snap.install('prometheus')
        assert snapd.installed == {}
        assert snapd.history == []

    def test_scoped_failure_only_matches_named_snap(self):
        error = snap.ConnectionError('boom', kind='charmlibs-snap-socket-not-found', value='')
        with Snapd(failures=[Failure('install', snap='grafana', error=error)]):
            snap.install('prometheus')  # Not scoped to prometheus: succeeds.
            with pytest.raises(snap.ConnectionError):
                snap.install('grafana')

    def test_times_exhausts_then_succeeds(self):
        error = snap.ChangeError(
            'run hook "post-refresh": exit status 1',
            kind='charmlibs-snap-change-error',
            value='42',
            status='Error',
        )
        failure = Failure('refresh', snap='prometheus', error=error, times=1)
        with Snapd([Snap('prometheus', revision='100')], failures=[failure]) as snapd:
            with pytest.raises(snap.ChangeError):
                snap.refresh('prometheus', revision=101)
            assert snapd.installed['prometheus'].revision == '100'  # Unchanged: it raised.
            snap.refresh('prometheus', revision=101)  # Budget exhausted: succeeds now.
        assert snapd.installed['prometheus'].revision == '101'


class TestHistoryOrdering:
    def test_records_path_taken_in_order(self):
        seeded = Snap('prometheus', channel='2/stable', services={'prometheus': 'active'})
        with Snapd([seeded]) as snapd:
            snap.stop('prometheus')
            snap.refresh('prometheus', channel='2/edge')
            snap.start('prometheus')
        assert snapd.history == [
            state.Stop(snap='prometheus', services=('prometheus',), disable=False),
            state.Refresh(snap='prometheus', channel='2/edge', revision=None),
            state.Start(snap='prometheus', services=('prometheus',), enable=False),
        ]


class TestConstructionValidation:
    def test_duplicate_snaps_raise_at_construction(self):
        with pytest.raises(SnapStateValidationError):
            Snapd([Snap('prometheus'), Snap('prometheus')])


class TestLifecycle:
    def test_single_use(self):
        snapd = Snapd()
        with snapd:
            pass
        with pytest.raises(RuntimeError):
            with snapd:
                pass

    def test_exit_restores_original_client_functions(self):
        original_get = _client.get
        with Snapd():
            assert _client.get is not original_get
        assert _client.get is original_get

    def test_unpatched_outside_context_raises_connection_error(self):
        # Sanity check that we're really testing against the real client outside the `with`.
        with pytest.raises(snap.ConnectionError):
            snap.info('prometheus')


# ---------------------------------------------------------------------------
# The endpoints below (conf, interfaces, aliases) have no caller in this fork of
# charmlibs.snap yet -- see the implementation log. These tests exercise the double's
# REST layer directly via charmlibs.snap._client, standing in for the not-yet-written
# _snapd_conf/_snapd_interfaces/_snapd_aliases wrapper functions.
# ---------------------------------------------------------------------------


class TestConfig:
    def test_get_all(self):
        with Snapd([Snap('lxd', config={'integer': 1, 'true': True})]):
            assert _client.get('/v2/snaps/lxd/conf') == {'integer': 1, 'true': True}

    def test_get_single_key(self):
        with Snapd([Snap('lxd', config={'integer': 1, 'true': True})]):
            assert _client.get('/v2/snaps/lxd/conf', query={'keys': 'integer'}) == {'integer': 1}

    def test_get_missing_key_raises_option_not_found(self):
        with Snapd([Snap('lxd', config={'integer': 1})]):
            with pytest.raises(OptionNotFoundError):
                _client.get('/v2/snaps/lxd/conf', query={'keys': 'missing'})

    def test_set(self):
        with Snapd([Snap('lxd')]) as snapd:
            _client.put('/v2/snaps/lxd/conf', body={'mykey': 'myval'})
        assert snapd.installed['lxd'].config == {'mykey': 'myval'}
        assert snapd.history == [state.ConfigSet(snap='lxd', values={'mykey': 'myval'})]

    def test_unset_via_null_value(self):
        with Snapd([Snap('lxd', config={'mykey': 'myval'})]) as snapd:
            _client.put('/v2/snaps/lxd/conf', body={'mykey': None})
        assert snapd.installed['lxd'].config == {}
        assert snapd.history == [state.ConfigUnset(snap='lxd', keys=('mykey',))]


class TestInterfaces:
    def test_connect_and_disconnect(self):
        plug_body = {
            'action': 'connect',
            'plugs': [{'snap': 'vlc', 'plug': 'mount-observe'}],
            'slots': [{'snap': 'lxd', 'slot': 'mount-observe'}],
        }
        with Snapd([Snap('vlc'), Snap('lxd')]) as snapd:
            _client.post('/v2/interfaces', body=plug_body)
            connection = Connection(plug=('vlc', 'mount-observe'), slot=('lxd', 'mount-observe'))
            assert connection in snapd.connections
            _client.post('/v2/interfaces', body={**plug_body, 'action': 'disconnect'})
            assert connection not in snapd.connections

    def test_connect_already_connected_raises(self):
        plug_body = {
            'action': 'connect',
            'plugs': [{'snap': 'vlc', 'plug': 'mount-observe'}],
            'slots': [{'snap': 'lxd', 'slot': 'mount-observe'}],
        }
        with Snapd([Snap('vlc'), Snap('lxd')]):
            _client.post('/v2/interfaces', body=plug_body)
            with pytest.raises(_InterfacesUnchangedError):
                _client.post('/v2/interfaces', body=plug_body)


class TestAliases:
    def test_alias_and_unalias(self):
        with Snapd([Snap('lxd', services={'lxc': 'active'})]) as snapd:
            _client.post(
                '/v2/aliases',
                body={'action': 'alias', 'snap': 'lxd', 'app': 'lxd.lxc', 'alias': 'lxc'},
            )
            assert snapd.installed['lxd'].aliases == {'lxc': 'lxc'}
            _client.post('/v2/aliases', body={'action': 'unalias', 'snap': 'lxd', 'alias': 'lxc'})
            assert snapd.installed['lxd'].aliases == {}

    def test_alias_unknown_app_raises_app_not_found(self):
        with Snapd([Snap('lxd', services={'lxc': 'active'})]):
            with pytest.raises(AppNotFoundError):
                _client.post(
                    '/v2/aliases',
                    body={'action': 'alias', 'snap': 'lxd', 'app': 'lxd.nope', 'alias': 'nope'},
                )
