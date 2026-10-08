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
    ChangeError,
    ChannelNotAvailableError,
    NeedsClassicError,
    NotInstalledError,
    NotInStoreError,
    OptionNotFoundError,
    RevisionNotAvailableError,
    _NotFoundError,
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

    def test_bare_risk_takes_latest_track(self):
        # Nothing is tracked yet, so there is no track to inherit. (The double doesn't model a
        # snap installed from a file, the one installed snap that tracks no channel.)
        with Snapd() as snapd:
            snap.ensure_installed('prometheus', 'edge')
        assert snapd.installed['prometheus'].channel == 'latest/edge'

    def test_already_installed_returns_false_and_is_not_recorded_twice(self):
        with Snapd([Snap('prometheus')]) as snapd:
            assert snap.install('prometheus') is False
        assert snapd.history == []


class TestInstallAuthoritative:
    def test_snap_not_in_store_raises(self):
        with Snapd(store=[StoreSnap('grafana')]):
            with pytest.raises(NotInStoreError):
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

    def test_revision_on_named_channel_keeps_channel(self):
        store_snap = StoreSnap('prometheus', channels={'2/stable': 100, '2/edge': 101})
        with Snapd(store=[store_snap]) as snapd:
            assert snap.install('prometheus', '2/edge', revision=101) is True
        installed = snapd.installed['prometheus']
        assert installed.channel == '2/edge'
        assert installed.revision == '101'

    def test_revision_not_on_named_channel_raises(self):
        # 101 is in the store, just not on 2/stable: snapd reports the pairing against the
        # channel, not the revision.
        store_snap = StoreSnap('prometheus', channels={'2/stable': 100, '2/edge': 101})
        with Snapd(store=[store_snap]) as snapd:
            with pytest.raises(ChannelNotAvailableError) as ctx:
                snap.install('prometheus', '2/stable', revision=101)
        assert type(ctx.value) is ChannelNotAvailableError
        assert ctx.value._kind == 'snap-channel-not-available'
        assert snapd.installed == {}

    def test_revision_without_channel_tracks_latest_stable(self):
        # The revision can come from any channel, but the snap tracks latest/stable regardless.
        store_snap = StoreSnap('prometheus', channels={'latest/stable': 100, '2/edge': 101})
        with Snapd(store=[store_snap]) as snapd:
            snap.install('prometheus', revision=101)
        installed = snapd.installed['prometheus']
        assert installed.channel == 'latest/stable'
        assert installed.revision == '101'

    def test_revision_on_no_channel_raises_revision_not_available(self):
        store_snap = StoreSnap('prometheus', channels={'latest/stable': 100})
        with Snapd(store=[store_snap]):
            with pytest.raises(RevisionNotAvailableError):
                snap.install('prometheus', revision=999)

    def test_bare_risk_takes_latest_track(self):
        # Nothing is tracked yet, so there is no track to inherit.
        store_snap = StoreSnap('prometheus', channels={'latest/edge': 5, '3.6/edge': 6})
        with Snapd(store=[store_snap]) as snapd:
            snap.ensure_installed('prometheus', 'edge')
        assert snapd.installed['prometheus'].channel == 'latest/edge'


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

    def test_authoritative_named_installed_revision_still_refreshes(self):
        # snapd runs a full refresh when a revision is named, even the installed one.
        store_snap = StoreSnap('prometheus', channels={'latest/stable': 100})
        with Snapd([Snap('prometheus', revision='100')], store=[store_snap]) as snapd:
            assert snap.refresh('prometheus', revision=100) is True
        assert snapd.installed['prometheus'].revision == '100'
        assert snapd.installed['prometheus'].channel == 'latest/stable'
        assert snapd.history == [state.Refresh(snap='prometheus', channel=None, revision='100')]

    def test_authoritative_channel_switch_to_same_revision_moves_tracking(self):
        # The channel alone changing is an update: snapd switches tracking without changing
        # the revision, rather than reporting snap-no-update-available.
        store_snap = StoreSnap('hello-world', channels={'latest/stable': 29, 'latest/edge': 29})
        seeded = Snap('hello-world', channel='latest/edge', revision='29')
        with Snapd([seeded], store=[store_snap]) as snapd:
            assert snap.refresh('hello-world', 'latest/stable') is True
        assert snapd.installed['hello-world'].revision == '29'
        assert snapd.installed['hello-world'].channel == 'latest/stable'

    def test_authoritative_update_available(self):
        store_snap = StoreSnap('prometheus', channels={'latest/stable': 101})
        with Snapd([Snap('prometheus', revision='100')], store=[store_snap]) as snapd:
            assert snap.refresh('prometheus') is True
        assert snapd.installed['prometheus'].revision == '101'

    @pytest.mark.parametrize('store', [False, True])
    def test_bare_risk_inherits_tracked_track(self, store: bool):
        store_snaps = (
            [StoreSnap('prometheus', channels={'3.6/stable': 100, '3.6/edge': 101})]
            if store
            else None
        )
        seeded = Snap('prometheus', channel='3.6/stable', revision='100')
        with Snapd([seeded], store=store_snaps) as snapd:
            assert snap.refresh('prometheus', 'edge') is True
        assert snapd.installed['prometheus'].channel == '3.6/edge'

    @pytest.mark.parametrize('store', [False, True])
    def test_explicit_track_and_risk_is_taken_as_is(self, store: bool):
        store_snaps = (
            [StoreSnap('prometheus', channels={'3.6/stable': 100, 'latest/edge': 101})]
            if store
            else None
        )
        seeded = Snap('prometheus', channel='3.6/stable', revision='100')
        with Snapd([seeded], store=store_snaps) as snapd:
            snap.refresh('prometheus', 'latest/edge')
        assert snapd.installed['prometheus'].channel == 'latest/edge'

    def test_bare_track_does_not_inherit_risk(self):
        with Snapd([Snap('prometheus', channel='3.6/edge')]) as snapd:
            snap.refresh('prometheus', '4.0')
        assert snapd.installed['prometheus'].channel == '4.0/stable'

    def test_authoritative_revision_on_named_channel(self):
        store_snap = StoreSnap('prometheus', channels={'2/stable': 100, '2/edge': 101})
        seeded = Snap('prometheus', channel='2/stable', revision='100')
        with Snapd([seeded], store=[store_snap]) as snapd:
            snap.refresh('prometheus', '2/edge', revision=101)
        assert snapd.installed['prometheus'].channel == '2/edge'
        assert snapd.installed['prometheus'].revision == '101'

    def test_authoritative_revision_not_on_named_channel_raises(self):
        store_snap = StoreSnap('prometheus', channels={'2/stable': 100, '2/edge': 101})
        seeded = Snap('prometheus', channel='2/edge', revision='101')
        with Snapd([seeded], store=[store_snap]) as snapd:
            with pytest.raises(ChannelNotAvailableError):
                snap.refresh('prometheus', '2/beta', revision=100)
        assert snapd.installed['prometheus'] == seeded

    def test_authoritative_revision_without_channel_keeps_tracking(self):
        store_snap = StoreSnap('prometheus', channels={'2/stable': 100, '2/edge': 101})
        seeded = Snap('prometheus', channel='2/stable', revision='100')
        with Snapd([seeded], store=[store_snap]) as snapd:
            snap.refresh('prometheus', revision=101)
        assert snapd.installed['prometheus'].channel == '2/stable'
        assert snapd.installed['prometheus'].revision == '101'


class TestEnsure:
    def test_installs_when_missing(self):
        with Snapd() as snapd:
            assert snap.ensure_installed('prometheus', channel='2/stable') is True
        assert snapd.installed['prometheus'].channel == '2/stable'
        assert snapd.history == [
            state.Install(snap='prometheus', channel='2/stable', revision=None, classic=False)
        ]

    def test_refreshes_on_channel_change(self):
        with Snapd([Snap('prometheus', channel='2/stable')]) as snapd:
            assert snap.ensure_installed('prometheus', channel='2/edge') is True
        assert snapd.installed['prometheus'].channel == '2/edge'
        assert isinstance(snapd.history[0], state.Refresh)

    def test_bare_risk_inherits_tracked_track(self):
        with Snapd([Snap('prometheus', channel='3.6/stable')]) as snapd:
            assert snap.ensure_installed('prometheus', 'edge') is True
            # Now on the channel ensure_installed resolves 'edge' to, so asking again with
            # update=False is a no-op rather than another refresh.
            assert snap.ensure_installed('prometheus', 'edge', update=False) is False
        assert snapd.installed['prometheus'].channel == '3.6/edge'
        assert len(snapd.history) == 1

    def test_same_revision_different_channel_switches_tracking(self):
        # One revision on two channels: ensuring the other channel still switches tracking.
        store_snap = StoreSnap('hello-world', channels={'latest/stable': 29, 'latest/edge': 29})
        with Snapd(store=[store_snap]) as snapd:
            snap.ensure_installed('hello-world', channel='latest/edge', revision=29)
            did_something = snap.ensure_installed(
                'hello-world', channel='latest/stable', revision=29
            )
            assert did_something is True
            info = snap.list_one('hello-world')
        assert info.revision == '29'
        assert info.tracking == 'latest/stable'
        assert snapd.history[-1] == state.Refresh(
            snap='hello-world', channel='latest/stable', revision='29'
        )

    def test_update_false_skips_refresh(self):
        with Snapd([Snap('prometheus', channel='2/stable')]) as snapd:
            assert snap.ensure_installed('prometheus', channel='2/stable', update=False) is False
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
            with pytest.raises(NotInstalledError):
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
        # /v2/apps answers app-not-found for a missing snap too, so start() probes
        # /v2/snaps/{snap} and narrows this to NotInstalledError.
        with Snapd():
            with pytest.raises(NotInstalledError):
                snap.start('prometheus')

    def test_start_snap_with_no_services_raises(self):
        # A whole-snap action on a snap with no services is app-not-found, not a no-op.
        with Snapd([Snap('prometheus')]):
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
        snap_ = Snap('prometheus', services={'prometheus': 'active'}, logs=entries)
        with Snapd([snap_]):
            result = snap.logs('prometheus')
        assert [e.message for e in result] == ['one', 'two']
        assert result[0].timestamp == entries[0].timestamp
        assert result[0].pid == 42
        assert result[0].sid == 'prometheus'

    def test_no_limit_filtering(self):
        entries = [self._entry(str(i), minute=i) for i in range(12)]
        snap_ = Snap('prometheus', services={'prometheus': 'active'}, logs=entries)
        with Snapd([snap_]):
            result = snap.logs('prometheus')  # default limit=10
        assert len(result) == 12  # Not sliced to 10: seeded logs are returned as-is.

    def test_missing_snap_raises_not_found(self):
        with Snapd():
            with pytest.raises(NotInstalledError):
                snap.logs('prometheus')

    def test_snap_with_no_services_raises_app_not_found(self):
        # Querying logs by name for a snap with no services is app-not-found.
        with Snapd([Snap('prometheus')]):
            with pytest.raises(AppNotFoundError) as ctx:
                snap.logs('prometheus')
        assert ctx.value._kind == 'app-not-found'

    def test_no_names_returns_all_installed(self):
        # A system-wide query names no snap, so it doesn't raise when no snap has services.
        a = Snap('a', logs=[self._entry('from-a')])
        b = Snap('b', logs=[self._entry('from-b')])
        with Snapd([a, b]):
            result = snap.logs()
        assert {e.message for e in result} == {'from-a', 'from-b'}


class TestFailureInjection:
    def test_wildcard_simulates_snapd_down(self):
        error = snap.ConnectionError('Could not connect to snapd')
        with Snapd(failures=[Failure('*', error=error)]) as snapd:
            with pytest.raises(snap.ConnectionError):
                snap.install('prometheus')
        assert snapd.installed == {}
        assert snapd.history == []

    def test_scoped_failure_only_matches_named_snap(self):
        error = snap.ConnectionError('boom')
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
        # Shows the tests above exercise the double: the client functions are replaced inside
        # the `with` and are the originals again (by identity) on exit.
        original_get = _client.get
        with Snapd():
            assert _client.get is not original_get
        assert _client.get is original_get


# ---------------------------------------------------------------------------
# conf, interfaces and aliases, through the real charmlibs.snap public functions.
# ---------------------------------------------------------------------------


class TestConfig:
    def test_get_all(self):
        with Snapd([Snap('lxd', config={'integer': 1, 'true': True})]):
            assert snap.get('lxd') == {'integer': 1, 'true': True}

    def test_get_single_key(self):
        with Snapd([Snap('lxd', config={'integer': 1, 'true': True})]):
            assert snap.get('lxd', 'integer') == {'integer': 1}

    def test_get_one(self):
        with Snapd([Snap('lxd', config={'integer': 1})]):
            assert snap.get_one('lxd', 'integer') == 1

    def test_get_missing_key_raises_option_not_found(self):
        with Snapd([Snap('lxd', config={'integer': 1})]):
            with pytest.raises(OptionNotFoundError):
                snap.get('lxd', 'missing')

    def test_get_not_installed_raises_not_installed(self):
        # The conf endpoint answers option-not-found for a missing snap too, so get() probes
        # /v2/snaps/{name} and narrows this to NotInstalledError.
        with Snapd():
            with pytest.raises(NotInstalledError):
                snap.get('lxd', 'missing')

    def test_set(self):
        with Snapd([Snap('lxd')]) as snapd:
            snap.set('lxd', {'mykey': 'myval'})
        assert snapd.installed['lxd'].config == {'mykey': 'myval'}
        assert snapd.history == [state.ConfigSet(snap='lxd', values={'mykey': 'myval'})]

    def test_unset(self):
        with Snapd([Snap('lxd', config={'mykey': 'myval'})]) as snapd:
            snap.unset('lxd', ['mykey'])
        assert snapd.installed['lxd'].config == {}
        assert snapd.history == [state.ConfigUnset(snap='lxd', keys=('mykey',))]

    def test_set_not_installed_raises(self):
        with Snapd():
            with pytest.raises(NotInstalledError):
                snap.set('lxd', {'mykey': 'myval'})

    def test_core_config_survives_without_a_core_snap(self):
        # 'system'/'core' configuration is served whether or not a 'core' snap is installed.
        with Snapd():
            snap.set('core', {'experimental.foo': True})
            assert snap.get_one('core', 'experimental.foo') is True
            snap.unset('core', ['experimental.foo'])
            assert snap.get('core') == {}

    @pytest.mark.parametrize('seeded', ['core', 'system'])
    @pytest.mark.parametrize('read_as', ['core', 'system'])
    def test_system_and_core_alias_a_seeded_snap(self, seeded: str, read_as: str):
        # Real snapd treats 'system' and 'core' as one configuration, so seeding a Snap under
        # either name must not split them.
        with Snapd([Snap(seeded, config={'experimental.foo': True})]):
            assert snap.get_one(read_as, 'experimental.foo') is True

    @pytest.mark.parametrize('write_as', ['core', 'system'])
    def test_writes_through_either_name_reach_the_seeded_snap(self, write_as: str):
        with Snapd([Snap('core')]) as snapd:
            snap.set(write_as, {'experimental.foo': True})
            assert snapd.installed['core'].config == {'experimental.foo': True}
            # Readable back under both names, not stranded in the no-core-snap store.
            assert snap.get_one('core', 'experimental.foo') is True
            assert snap.get_one('system', 'experimental.foo') is True
            snap.unset(write_as, ['experimental.foo'])
            assert snapd.installed['core'].config == {}

    @pytest.mark.parametrize('read_as', ['core', 'system'])
    def test_removing_core_drops_the_stored_system_config(self, read_as: str):
        # Real snapd drops stored system configuration when core is removed, so a value set
        # while core was absent must not reappear after core is installed and removed.
        with Snapd() as snapd:
            snap.set('core', {'experimental.foo': True})
            snap.install('core')
            snap.remove('core')
            assert snapd.installed == {}
            assert snap.get(read_as) == {}

    def test_removing_system_is_a_no_op(self):
        # 'system' names core's configuration, not a snap, so removing it must not uninstall
        # core or clear its configuration.
        with Snapd() as snapd:
            snap.set('core', {'experimental.foo': True})
            snap.install('core')
            assert snap.remove('system') is False
            assert list(snapd.installed) == ['core']
            snap.set('system', {'experimental.bar': True})
            assert snap.get_one('core', 'experimental.bar') is True

    def test_removing_an_ordinary_snap_leaves_the_system_config_alone(self):
        # The clearing above is scoped to core/system, not to every removal.
        with Snapd([Snap('prometheus')]):
            snap.set('core', {'experimental.foo': True})
            snap.remove('prometheus')
            assert snap.get_one('core', 'experimental.foo') is True

    def test_core_wins_when_a_test_seeds_both_names(self):
        # Real snapd has no 'system' snap, but the double must still not serve two
        # configurations if a test seeds both.
        with Snapd([Snap('core', config={'k': 'from-core'}), Snap('system', config={'k': 'x'})]):
            assert snap.get_one('system', 'k') == 'from-core'
            assert snap.get_one('core', 'k') == 'from-core'


class TestInterfaces:
    def test_connect_and_disconnect(self):
        with Snapd([Snap('vlc'), Snap('lxd')]) as snapd:
            snap.connect(('vlc', 'mount-observe'), ('lxd', 'mount-observe'))
            connection = Connection(plug=('vlc', 'mount-observe'), slot=('lxd', 'mount-observe'))
            assert connection in snapd.connections
            snap.disconnect(('vlc', 'mount-observe'), ('lxd', 'mount-observe'))
            assert connection not in snapd.connections

    def test_connect_already_connected_does_not_raise(self):
        # snapd's connect is idempotent (unlike disconnect), so reconnecting succeeds silently.
        with Snapd([Snap('vlc'), Snap('lxd')]) as snapd:
            snap.connect(('vlc', 'mount-observe'), ('lxd', 'mount-observe'))
            snap.connect(('vlc', 'mount-observe'), ('lxd', 'mount-observe'))  # Does not raise.
        connection = Connection(plug=('vlc', 'mount-observe'), slot=('lxd', 'mount-observe'))
        assert connection in snapd.connections

    def test_disconnect_one_sided_not_connected_does_not_raise(self):
        with Snapd([Snap('vlc')]):
            snap.disconnect(('vlc', 'mount-observe'))  # Should not raise.

    def test_disconnect_two_sided_not_connected_raises(self):
        # Unlike connect, a two-sided disconnect of an unconnected pair raises ('not connected',
        # not interfaces-unchanged).
        with Snapd([Snap('vlc'), Snap('lxd')]):
            with pytest.raises(snap.APIError):
                snap.disconnect(('vlc', 'mount-observe'), ('lxd', 'mount-observe'))

    def test_connect_not_installed_raises(self):
        with Snapd([Snap('vlc')]):
            with pytest.raises(NotInstalledError):
                snap.connect(('vlc', 'mount-observe'), ('lxd', 'mount-observe'))


class TestAliases:
    def test_alias_and_unalias(self):
        with Snapd([Snap('lxd', services={'lxc': 'active'})]) as snapd:
            snap.alias('lxd', 'lxc', 'testlxc')
            assert snapd.installed['lxd'].aliases == {'testlxc': 'lxc'}
            snap.unalias('testlxc')
            assert snapd.installed['lxd'].aliases == {}

    def test_alias_unknown_app_raises_change_error(self):
        # Aliasing a nonexistent app is an async change failure, not a synchronous
        # AppNotFoundError.
        with Snapd([Snap('lxd', services={'lxc': 'active'})]):
            with pytest.raises(ChangeError):
                snap.alias('lxd', 'nope', 'testnope')

    def test_alias_not_installed_raises(self):
        with Snapd():
            with pytest.raises(NotInstalledError):
                snap.alias('lxd', 'lxc', 'testlxc')

    def test_alias_claimed_by_another_snap_raises(self):
        with Snapd([
            Snap('lxd', services={'lxc': 'active'}),
            Snap('other', services={'cmd': 'active'}),
        ]) as snapd:
            snap.alias('lxd', 'lxc', 'shared-alias')
            with pytest.raises(ChangeError):
                snap.alias('other', 'cmd', 'shared-alias')
        assert snapd.installed['lxd'].aliases == {'shared-alias': 'lxc'}

    def test_alias_named_after_installed_snap_raises(self):
        # An alias equal to any installed snap's name conflicts with its command namespace,
        # including the snap being aliased.
        with Snapd([Snap('lxd', services={'lxc': 'active'})]):
            with pytest.raises(ChangeError):
                snap.alias('lxd', 'lxc', 'lxd')

    def test_unalias_unknown_alias_raises(self):
        with Snapd([Snap('lxd', services={'lxc': 'active'})]):
            with pytest.raises(snap.APIError):
                snap.unalias('never-created')


# ---------------------------------------------------------------------------
# Behaviours that match real snapd. Some tests assert at the raw /v2 layer, because the
# public functions narrow those errors to NotInstalledError and would hide a regression.
# ---------------------------------------------------------------------------


class TestOracleRawAppsNotInstalled:
    """The two /v2/apps request forms are not the same error."""

    def test_snap_alone_is_snap_not_found(self):
        with Snapd():
            with pytest.raises(_NotFoundError) as ctx:
                _client.post('/v2/apps', body={'action': 'start', 'names': ['prometheus']})
        assert ctx.value._kind == 'snap-not-found'
        assert ctx.value.message == 'snap "prometheus" not found'

    def test_snap_with_service_is_app_not_found(self):
        with Snapd():
            with pytest.raises(AppNotFoundError) as ctx:
                _client.post('/v2/apps', body={'action': 'start', 'names': ['prometheus.web']})
        assert ctx.value._kind == 'app-not-found'
        assert ctx.value.message == 'snap "prometheus" has no service "web"'

    def test_installed_snap_lacking_the_service_is_indistinguishable(self):
        # snapd gives the same kind and message whether the snap is absent or merely lacks the
        # service, which is why the library probes /v2/snaps to tell them apart.
        with Snapd([Snap('prometheus', services={'prometheus': 'active'})]):
            with pytest.raises(AppNotFoundError) as ctx:
                _client.post('/v2/apps', body={'action': 'start', 'names': ['prometheus.web']})
        assert ctx.value._kind == 'app-not-found'
        assert ctx.value.message == 'snap "prometheus" has no service "web"'

    def test_public_start_still_narrows_to_not_installed(self):
        # The public function still narrows the raw error to NotInstalledError.
        with Snapd():
            with pytest.raises(NotInstalledError):
                snap.start('prometheus')


class TestOracleEmptyPlug:
    """An empty plug side is an error; an empty slot side auto-resolves."""

    def test_empty_plug_snap_raises(self):
        with Snapd([Snap('prometheus')]) as snapd:
            with pytest.raises(snap.APIError) as ctx:
                snap.connect(('', 'metrics'), ('prometheus', 'metrics'))
            assert snapd.connections == set()
        assert ctx.value.message == 'cannot resolve connection, plug snap name is empty'

    def test_empty_plug_name_raises(self):
        with Snapd([Snap('prometheus')]) as snapd:
            with pytest.raises(snap.APIError) as ctx:
                snap.connect(('prometheus', ''), ('prometheus', 'metrics'))
            assert snapd.connections == set()
        assert ctx.value.message == 'cannot resolve connection, plug name is empty'

    def test_plug_snap_is_checked_before_plug_name(self):
        # Both empty: snapd reports the snap, never reaching the name check.
        with Snapd():
            with pytest.raises(snap.APIError) as ctx:
                snap.connect(('', ''), ('', ''))
        assert ctx.value.message == 'cannot resolve connection, plug snap name is empty'

    def test_empty_slot_snap_still_auto_resolves(self):
        # The asymmetry: only the plug side is rejected when empty.
        with Snapd([Snap('prometheus')]) as snapd:
            snap.connect(('prometheus', 'home'), ('', 'home'))
        assert Connection(plug=('prometheus', 'home'), slot=('', 'home')) in snapd.connections


class TestOracleBareRefreshFollowsTrackedChannel:
    """A refresh with no channel follows the tracked channel, not latest."""

    def test_bare_refresh_of_a_current_non_latest_track_reports_no_update(self):
        # Tracking 3/stable with no latest/stable in the store: resolving against latest/stable
        # would raise ChannelNotAvailableError instead of returning falsy.
        installed = Snap('juju', channel='3/stable', revision=36041)
        store = StoreSnap('juju', channels={'3/stable': 36041, '3/edge': 36100})
        with Snapd([installed], store=[store]):
            assert not snap.refresh('juju')

    def test_bare_refresh_takes_the_tracked_channels_head(self):
        installed = Snap('juju', channel='3/stable', revision=36041)
        store = StoreSnap('juju', channels={'3/stable': 36500, 'latest/stable': 99999})
        with Snapd([installed], store=[store]) as snapd:
            assert snap.refresh('juju')
        assert snapd.installed['juju'].revision == '36500'
        assert snapd.installed['juju'].channel == '3/stable'

    def test_explicit_channel_still_wins_over_the_tracked_one(self):
        installed = Snap('juju', channel='3/stable', revision=36041)
        store = StoreSnap('juju', channels={'3/stable': 36041, '3/edge': 36100})
        with Snapd([installed], store=[store]) as snapd:
            assert snap.refresh('juju', channel='3/edge')
        assert snapd.installed['juju'].revision == '36100'
