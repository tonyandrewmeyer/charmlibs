# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

from __future__ import annotations

import pytest

from charmlibs import snap
from charmlibs.snap_testing import _consistency as consistency
from charmlibs.snap_testing import _state as state


class TestSnapValidation:
    def test_valid_snap_passes(self):
        consistency.validate_snap(state.Snap('prometheus', channel='2/stable'))

    @pytest.mark.parametrize('name', ['', 'has/slash', ' leading-space', 'trailing-space '])
    def test_invalid_name_raises(self, name: str):
        with pytest.raises(consistency.SnapStateValidationError):
            consistency.validate_snap(state.Snap(name))

    @pytest.mark.parametrize('channel', ['2/garbage', '/stable', '2/stable/'])
    def test_invalid_channel_raises(self, channel: str):
        with pytest.raises(consistency.SnapStateValidationError):
            consistency.validate_snap(state.Snap('prometheus', channel=channel))

    def test_alias_must_name_existing_service(self):
        with pytest.raises(consistency.SnapStateValidationError):
            consistency.validate_snap(
                state.Snap(
                    'prometheus',
                    services={'prometheus': 'active'},
                    aliases={'promql': 'nonexistent'},
                )
            )

    def test_alias_naming_existing_service_passes(self):
        consistency.validate_snap(
            state.Snap(
                'prometheus',
                services={'prometheus': 'active'},
                aliases={'promql': 'prometheus'},
            )
        )


class TestWorldValidation:
    def test_duplicate_snap_names_raise(self):
        with pytest.raises(consistency.SnapStateValidationError, match='duplicate'):
            consistency.validate_world(
                installed=[state.Snap('prometheus'), state.Snap('prometheus')],
                store=None,
                connections=(),
                failures=(),
            )

    def test_connection_naming_unknown_snap_raises(self):
        connection = state.Connection(plug=('lxd', 'lxd-support'), slot=('snapd', 'lxd-support'))
        with pytest.raises(consistency.SnapStateValidationError, match='not in installed'):
            consistency.validate_world(
                installed=[], store=None, connections=[connection], failures=()
            )

    def test_connection_naming_installed_snap_passes(self):
        # Both endpoints must be in `installed` per design.md 6.3 -- including the 'snapd'
        # pseudo-snap that plugs typically connect to, which a test must seed explicitly.
        connection = state.Connection(plug=('lxd', 'lxd-support'), slot=('snapd', 'lxd-support'))
        consistency.validate_world(
            installed=[state.Snap('lxd'), state.Snap('snapd')],
            store=None,
            connections=[connection],
            failures=(),
        )

    def test_unknown_failure_action_raises(self):
        error = snap.ConnectionError('boom', kind='charmlibs-snap-socket-not-found', value='')
        with pytest.raises(consistency.SnapStateValidationError, match='not a known action'):
            consistency.validate_world(
                installed=[],
                store=None,
                connections=(),
                failures=[state.Failure('not-a-real-action', error=error)],
            )

    def test_wildcard_failure_action_passes(self):
        error = snap.ConnectionError('boom', kind='charmlibs-snap-socket-not-found', value='')
        consistency.validate_world(
            installed=[], store=None, connections=(), failures=[state.Failure('*', error=error)]
        )

    def test_store_snap_bad_channel_raises(self):
        with pytest.raises(consistency.SnapStateValidationError):
            consistency.validate_world(
                installed=[],
                store=[state.StoreSnap('grafana', channels={'2/garbage': 1})],
                connections=(),
                failures=(),
            )
