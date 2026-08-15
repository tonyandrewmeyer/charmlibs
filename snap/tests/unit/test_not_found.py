# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""The library-wide contract for an absent snap: a subclass of _NotFoundError, never the base.

snapd sends the same ``snap-not-found`` kind whether a snap is missing from the system or from the
store, and only the message differs, with wording that varies by endpoint. So the client raises
the base type and the function that made the request narrows it, since only that function knows
what it asked for. These tests hold that rule to every public function.

Driven through ``charmlibs.snap_testing.Snapd`` (step 6 of the snaptest plan) rather than a
canned ``_NotFoundError`` replayed through a mocked ``_client``: an empty ``Snapd()`` naturally
answers "snap not found" for every one of these calls the same way real snapd does, through the
same code paths -- ``check_installed`` probes included -- that a charm test exercises. This is a
stronger check than the mock version it replaces: it fails if the double's own narrowing ever
drifts from what these functions actually do, not just if the functions regress.
"""

from __future__ import annotations

import inspect
import typing

import pytest

from charmlibs import snap
from charmlibs.snap._errors import NotInstalledError, NotInStoreError
from charmlibs.snap_testing import Snap, Snapd

if typing.TYPE_CHECKING:
    from collections.abc import Callable

# Every public function must be listed here, in one of:
# 1. EXCLUDE if snapd never sends snap-not-found.
# 2. CALLS with a call that reaches the store.
# List also in one of:
# 1. DOES_NOT_RAISE if snap-not-found is handled but not raised.
# 2. RAISES_NOT_IN_STORE if snap-not-found becomes NotInStoreError.
# Otherwise the call is assumed to raise NotInstalledError.
EXCLUDE = {'alias', 'unalias', 'unhold'}
CALLS: dict[str, Callable[[], object]] = {
    'connect': lambda: snap.connect(('lxd', 'home')),
    'disconnect': lambda: snap.disconnect(('lxd', 'home')),
    'ensure_installed': lambda: snap.ensure_installed('lxd'),
    'get': lambda: snap.get('lxd'),
    'get_one': lambda: snap.get_one('lxd', 'mykey'),
    'hold': lambda: snap.hold('lxd'),
    'install': lambda: snap.install('lxd'),
    'list_one': lambda: snap.list_one('lxd'),
    'logs': lambda: snap.logs('lxd'),
    'refresh': lambda: snap.refresh('lxd'),
    'remove': lambda: snap.remove('lxd'),
    'restart': lambda: snap.restart('lxd'),
    'set': lambda: snap.set('lxd', {'mykey': 'myval'}),
    'start': lambda: snap.start('lxd'),
    'stop': lambda: snap.stop('lxd'),
    'unset': lambda: snap.unset('lxd', ['mykey']),
}
DOES_NOT_RAISE = {'remove'}  # catches _NotFoundError but doesn't raise
RAISES_NOT_IN_STORE = {'ensure_installed', 'install'}


def test_every_public_function_is_accounted_for():
    public = {name for name in snap.__all__ if inspect.isfunction(getattr(snap, name))}
    assert public == set(CALLS) | EXCLUDE


@pytest.mark.parametrize('name', sorted(set(CALLS) - DOES_NOT_RAISE - RAISES_NOT_IN_STORE))
def test_raises_not_installed_error(name: str):
    # No snaps installed and no store described: 'lxd' is simply absent. Every function listed
    # here operates on an installed snap, so each should narrow snapd's snap-not-found response
    # to NotInstalledError.
    with Snapd():
        with pytest.raises(NotInstalledError) as exc:
            CALLS[name]()
    assert type(exc.value) is NotInstalledError, 'Must narrow to a subtype, not _NotFoundError.'


@pytest.mark.parametrize('name', sorted(RAISES_NOT_IN_STORE))
def test_raises_not_in_store_error(name: str):
    # An authoritative store that has never heard of 'lxd' -- the sense install() and
    # ensure_installed() narrow snap-not-found to.
    with Snapd(store=[]):
        with pytest.raises(NotInStoreError) as exc:
            CALLS[name]()
    assert type(exc.value) is NotInStoreError, 'Must narrow to a subtype, not _NotFoundError.'


@pytest.mark.parametrize('name', sorted(DOES_NOT_RAISE))
def test_does_not_raise(name: str):
    with Snapd():
        CALLS[name]()  # Does not raise.


def test_refresh_also_raises_not_in_store_error():
    # refresh() is the one operation where both senses of snap-not-found are reachable: 'lxd' is
    # installed locally, so the not-installed probe finds it, but the (authoritative, empty)
    # store no longer offers it -- the *other* sense of not-found, narrowed to NotInStoreError
    # rather than NotInstalledError.
    with Snapd([Snap('lxd')], store=[]):
        with pytest.raises(NotInStoreError) as exc:
            snap.refresh('lxd')
    assert type(exc.value) is NotInStoreError, 'Must narrow to a subtype, not _NotFoundError.'
