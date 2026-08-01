# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

from __future__ import annotations

import datetime

import pytest

from charmlibs import snap
from charmlibs.snap_testing import _state as state


class TestSnap:
    def test_defaults(self):
        s = state.Snap('prometheus')
        assert s.name == 'prometheus'
        assert s.channel == 'latest/stable'
        assert s.revision == '1'
        assert s.version == '1.0'
        assert s.classic is False
        assert s.hold is None
        assert s.services == {}
        assert s.config == {}
        assert s.aliases == {}
        assert s.logs == ()

    def test_channel_is_normalized(self):
        assert state.Snap('prometheus', channel='edge').channel == 'latest/edge'
        assert state.Snap('prometheus', channel='2/stable').channel == '2/stable'

    def test_revision_accepts_int(self):
        assert state.Snap('prometheus', revision=100).revision == '100'

    def test_services_and_config_are_copied_not_aliased(self):
        services: dict[str, state.ServiceStatus] = {'prometheus': 'active'}
        s = state.Snap('prometheus', services=services)
        services['prometheus'] = 'inactive'
        assert s.services == {'prometheus': 'active'}

    def test_equality(self):
        a = state.Snap('prometheus', channel='2/stable', services={'prometheus': 'active'})
        b = state.Snap('prometheus', channel='2/stable', services={'prometheus': 'active'})
        assert a == b

    def test_logs_accepts_log_entries(self):
        entry = snap.LogEntry(
            timestamp=datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc),
            sid='prometheus',
            pid=1,
            message='hello',
        )
        s = state.Snap('prometheus', logs=[entry])
        assert s.logs == (entry,)


class TestReplace:
    def test_replace_preserves_untouched_fields(self):
        s = state.Snap('prometheus', channel='2/stable', version='2.53.0')
        replaced = state.replace(s, revision='101')
        assert replaced.name == 'prometheus'
        assert replaced.channel == '2/stable'
        assert replaced.version == '2.53.0'
        assert replaced.revision == '101'


class TestStoreSnap:
    def test_defaults(self):
        ss = state.StoreSnap('grafana')
        assert ss.channels == {'latest/stable': 1}
        assert ss.version == '1.0'
        assert ss.classic is False
        assert ss.services == ()
        assert ss.daemon_services == ()

    def test_channels_are_normalized(self):
        ss = state.StoreSnap('grafana', channels={'edge': 5})
        assert ss.channels == {'latest/edge': 5}


class TestFailure:
    def test_defaults(self):
        error = snap.ConnectionError('boom', kind='charmlibs-snap-socket-not-found', value='')
        f = state.Failure('*', error=error)
        assert f.snap is None
        assert f.times is None

    def test_scoped_to_snap(self):
        error = snap.ChangeError('boom', kind='charmlibs-snap-change-error', value='42')
        f = state.Failure('refresh', snap='prometheus', error=error, times=1)
        assert f.snap == 'prometheus'
        assert f.times == 1


def test_connection_is_hashable_and_comparable():
    a = state.Connection(plug=('lxd', 'lxd-support'), slot=('snapd', 'lxd-support'))
    b = state.Connection(plug=('lxd', 'lxd-support'), slot=('snapd', 'lxd-support'))
    assert a == b
    assert {a, b} == {a}


@pytest.mark.parametrize(
    'op',
    [
        state.Install(snap='x', channel=None, revision=None, classic=False),
        state.Refresh(snap='x', channel='2/edge', revision=None),
        state.Remove(snap='x', purge=True),
        state.Start(snap='x', services=('x',), enable=False),
        state.Stop(snap='x', services=('x',), disable=False),
    ],
)
def test_operations_are_frozen_and_comparable(op: state.Operation):
    with pytest.raises(AttributeError):
        op.snap = 'y'  # type: ignore[misc]
    assert op == op
