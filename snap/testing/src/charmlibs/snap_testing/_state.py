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

"""The state model for the simulated snapd: what a test can seed and assert on."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Literal

from charmlibs.snap import _utils

if TYPE_CHECKING:
    import datetime
    from collections.abc import Iterable, Mapping, Sequence

    from charmlibs import snap

ServiceStatus = Literal['active', 'inactive']


@dataclasses.dataclass(frozen=True, kw_only=True, init=False)
class Snap:
    """A snap installed on the simulated machine."""

    name: str
    channel: str
    revision: str
    version: str
    classic: bool
    hold: datetime.datetime | None
    services: Mapping[str, ServiceStatus]
    config: Mapping[str, Any]
    aliases: Mapping[str, str]
    logs: Sequence[snap.LogEntry]

    def __init__(
        self,
        name: str,
        *,
        channel: str = 'latest/stable',
        revision: int | str = 1,
        version: str = '1.0',
        classic: bool = False,
        hold: datetime.datetime | None = None,
        services: Mapping[str, ServiceStatus] = {},
        config: Mapping[str, Any] = {},
        aliases: Mapping[str, str] = {},
        logs: Iterable[snap.LogEntry] = (),
    ) -> None:
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'channel', _utils.normalize_channel(channel))
        object.__setattr__(self, 'revision', str(revision))
        object.__setattr__(self, 'version', version)
        object.__setattr__(self, 'classic', classic)
        object.__setattr__(self, 'hold', hold)
        object.__setattr__(self, 'services', dict(services))
        object.__setattr__(self, 'config', dict(config))
        object.__setattr__(self, 'aliases', dict(aliases))
        object.__setattr__(self, 'logs', tuple(logs))

    def __hash__(self) -> int:
        # Mapping/Sequence fields make the default dataclass hash unusable; Snap is compared
        # by == (installed is a Mapping, not a set), so identity hashing is sufficient here.
        return id(self)


class _Unset:
    pass


_UNSET = _Unset()


def replace(
    snap: Snap,
    *,
    channel: str | _Unset = _UNSET,
    revision: str | _Unset = _UNSET,
    version: str | _Unset = _UNSET,
    classic: bool | _Unset = _UNSET,
    hold: datetime.datetime | _Unset | None = _UNSET,
    services: Mapping[str, ServiceStatus] | _Unset = _UNSET,
    config: Mapping[str, Any] | _Unset = _UNSET,
    aliases: Mapping[str, str] | _Unset = _UNSET,
) -> Snap:
    """Build a new :class:`Snap`, applying changes on top of ``snap``'s current fields."""
    return Snap(
        snap.name,
        channel=snap.channel if isinstance(channel, _Unset) else channel,
        revision=snap.revision if isinstance(revision, _Unset) else revision,
        version=snap.version if isinstance(version, _Unset) else version,
        classic=snap.classic if isinstance(classic, _Unset) else classic,
        hold=snap.hold if isinstance(hold, _Unset) else hold,
        services=snap.services if isinstance(services, _Unset) else services,
        config=snap.config if isinstance(config, _Unset) else config,
        aliases=snap.aliases if isinstance(aliases, _Unset) else aliases,
        logs=snap.logs,
    )


@dataclasses.dataclass(frozen=True, kw_only=True, init=False)
class StoreSnap:
    """A snap available in the simulated store."""

    name: str
    channels: Mapping[str, int]
    version: str
    classic: bool
    services: Sequence[str]
    daemon_services: Sequence[str]

    def __init__(
        self,
        name: str,
        *,
        channels: Mapping[str, int] = {'latest/stable': 1},
        version: str = '1.0',
        classic: bool = False,
        services: Iterable[str] = (),
        daemon_services: Iterable[str] = (),
    ) -> None:
        object.__setattr__(self, 'name', name)
        object.__setattr__(
            self,
            'channels',
            {_utils.normalize_channel(c): r for c, r in channels.items()},
        )
        object.__setattr__(self, 'version', version)
        object.__setattr__(self, 'classic', classic)
        object.__setattr__(self, 'services', tuple(services))
        object.__setattr__(self, 'daemon_services', tuple(daemon_services))

    def __hash__(self) -> int:
        return id(self)


@dataclasses.dataclass(frozen=True)
class Connection:
    """A connected plug/slot pair."""

    plug: tuple[str, str]
    slot: tuple[str, str]


@dataclasses.dataclass(frozen=True, kw_only=True, init=False)
class Failure:
    """An error to raise instead of performing an operation."""

    action: str
    snap: str | None
    error: snap.Error
    times: int | None

    def __init__(
        self,
        action: str,
        *,
        snap: str | None = None,
        error: snap.Error,
        times: int | None = None,
    ) -> None:
        object.__setattr__(self, 'action', action)
        object.__setattr__(self, 'snap', snap)
        object.__setattr__(self, 'error', error)
        object.__setattr__(self, 'times', times)

    def __hash__(self) -> int:
        return id(self)


#####################
# Operation history #
#####################


@dataclasses.dataclass(frozen=True)
class Operation:
    """Base class for recorded operations."""

    snap: str


@dataclasses.dataclass(frozen=True)
class Install(Operation):
    channel: str | None
    revision: str | None
    classic: bool


@dataclasses.dataclass(frozen=True)
class Refresh(Operation):
    channel: str | None
    revision: str | None


@dataclasses.dataclass(frozen=True)
class Remove(Operation):
    purge: bool


@dataclasses.dataclass(frozen=True)
class Hold(Operation):
    until: datetime.datetime | None
    """``None`` for an indefinite hold (snapd's ``'forever'``); otherwise the resolved time."""


@dataclasses.dataclass(frozen=True)
class Unhold(Operation):
    pass


@dataclasses.dataclass(frozen=True)
class Start(Operation):
    services: tuple[str, ...]
    enable: bool


@dataclasses.dataclass(frozen=True)
class Stop(Operation):
    services: tuple[str, ...]
    disable: bool


@dataclasses.dataclass(frozen=True)
class Restart(Operation):
    services: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class ConfigGet(Operation):
    keys: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class ConfigSet(Operation):
    values: Mapping[str, Any]


@dataclasses.dataclass(frozen=True)
class ConfigUnset(Operation):
    keys: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class Connect(Operation):
    plug: tuple[str, str]
    slot: tuple[str, str]


@dataclasses.dataclass(frozen=True)
class Disconnect(Operation):
    plug: tuple[str, str]
    slot: tuple[str, str]


@dataclasses.dataclass(frozen=True)
class Alias(Operation):
    app: str
    alias: str


@dataclasses.dataclass(frozen=True)
class Unalias(Operation):
    alias: str | None
    """The alias removed, or ``None`` if every alias for the snap was removed."""


@dataclasses.dataclass(frozen=True)
class Logs(Operation):
    """A ``snap.logs()`` call. ``snap`` is the comma-joined queried names, or ``''`` for all."""

    limit: int | None
