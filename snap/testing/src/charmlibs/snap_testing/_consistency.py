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

"""Reject :class:`Snapd` inputs describing a state the real snapd could not be in.

Mirrors the spirit of ``scenario._consistency_checker``: validate at construction time,
so a bad test setup fails loudly instead of producing a confusing result several layers down.

design.md section 6.3 asks for two checks to reuse the real library's own validation:
``charmlibs.snap._utils.snap_path_segment`` for names, and a channel format check via
``normalize_channel``. The fork sync (see the implementation log) brought in
``snap_path_segment``, which this module now delegates to. ``normalize_channel`` still does not
raise on malformed input -- it silently reformats whatever string it's given -- so there is still
no real helper to delegate the channel check to; this module keeps its own, deliberately
narrower, stand-in for that one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from charmlibs.snap import _utils

if TYPE_CHECKING:
    from collections.abc import Iterable

    from charmlibs.snap_testing import _state as state

_RISKS = frozenset({'stable', 'candidate', 'beta', 'edge'})

_KNOWN_ACTIONS = frozenset({
    'install',
    'refresh',
    'remove',
    'hold',
    'unhold',
    'start',
    'stop',
    'restart',
    'get',
    'set',
    'unset',
    'connect',
    'disconnect',
    'alias',
    'unalias',
    'logs',
})


class SnapStateValidationError(Exception):
    """Raised when a :class:`Snapd` is constructed with an inconsistent or invalid state."""


def _is_valid_name(name: str) -> bool:
    try:
        _utils.snap_path_segment(name)
    except ValueError:
        return False
    return True


def _is_valid_channel(channel: str) -> bool:
    if not channel:
        return False
    parts = channel.split('/')
    if len(parts) > 3:
        return False
    if len(parts) == 1:
        # A bare risk (e.g. 'edge') or bare track: both are valid, normalize_channel handles it.
        return bool(parts[0])
    track, risk, *branch = parts
    if not track or risk not in _RISKS:
        return False
    return not branch or bool(branch[0])


def validate_snap(snap: state.Snap) -> None:
    """Validate a single :class:`Snap`'s internal consistency."""
    if not _is_valid_name(snap.name):
        raise SnapStateValidationError(f'{snap.name!r} is not a valid snap name')
    if not _is_valid_channel(snap.channel):
        raise SnapStateValidationError(
            f'{snap.channel!r} is not a valid channel for snap {snap.name!r}'
        )
    for alias, app in snap.aliases.items():
        if app not in snap.services:
            raise SnapStateValidationError(
                f'alias {alias!r} for snap {snap.name!r} names app {app!r},'
                f' which is not in its services {sorted(snap.services)}'
            )


def validate_store_snap(store_snap: state.StoreSnap) -> None:
    """Validate a single :class:`StoreSnap`'s internal consistency."""
    if not _is_valid_name(store_snap.name):
        raise SnapStateValidationError(f'{store_snap.name!r} is not a valid snap name')
    for channel in store_snap.channels:
        if not _is_valid_channel(channel):
            raise SnapStateValidationError(
                f'{channel!r} is not a valid channel for store snap {store_snap.name!r}'
            )


def validate_world(
    *,
    installed: Iterable[state.Snap],
    store: Iterable[state.StoreSnap] | None,
    connections: Iterable[state.Connection],
    failures: Iterable[state.Failure],
) -> None:
    """Validate a :class:`Snapd`'s inputs together, once each is known to be valid alone."""
    seen: set[str] = set()
    for snap in installed:
        if snap.name in seen:
            raise SnapStateValidationError(f'duplicate snap {snap.name!r} in installed')
        seen.add(snap.name)
        validate_snap(snap)

    if store is not None:
        for store_snap in store:
            validate_store_snap(store_snap)

    for connection in connections:
        for endpoint, kind in ((connection.plug, 'plug'), (connection.slot, 'slot')):
            snap_name = endpoint[0]
            if snap_name not in seen:
                raise SnapStateValidationError(
                    f'connection {kind} names snap {snap_name!r}, which is not in installed'
                )

    for failure in failures:
        if failure.action != '*' and failure.action not in _KNOWN_ACTIONS:
            raise SnapStateValidationError(
                f'{failure.action!r} is not a known action or "*"'
                f' (known actions: {sorted(_KNOWN_ACTIONS)})'
            )
