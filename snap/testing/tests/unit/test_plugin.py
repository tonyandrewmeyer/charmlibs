# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

from __future__ import annotations

from typing import TYPE_CHECKING

from charmlibs import snap

if TYPE_CHECKING:
    from charmlibs.snap_testing import Snapd


def test_snapd_fixture_is_entered(snapd: Snapd):
    snap.install('prometheus')
    assert snapd.installed['prometheus'].name == 'prometheus'


def test_snapd_fixture_can_be_entered_again_by_the_test(snapd: Snapd):
    with snapd:
        snap.install('prometheus')
    snap.install('grafana')
    assert set(snapd.installed) == {'prometheus', 'grafana'}
