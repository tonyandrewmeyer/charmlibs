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

"""The fake snapd REST layer: a stateful router standing in for ``charmlibs.snap._client``.

Each public method here has the exact signature of its ``_client`` counterpart
(``get``, ``get_logs``, ``post``, ``put``) and the same return contract: the already-decoded
``result`` (or resolved async ``data``) of a real response, or a raised :class:`snap.Error`
subclass. There is no HTTP envelope and no async polling to simulate -- the double substitutes
below that layer, per design.md section 9.

Endpoint coverage matches design.md section 10. ``/v2/snaps/{name}``, ``/v2/apps`` and
``/v2/logs`` are exercised today by ``charmlibs.snap``'s real public functions in this checkout.
``/v2/snaps/{name}/conf``, ``/v2/interfaces`` and ``/v2/aliases`` are modelled per the fixtures
and the standard snapd wire format, but have no library caller to verify the request shape
against yet -- see the implementation log.
"""

from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING, Any

from charmlibs.snap import _utils
from charmlibs.snap._errors import (
    AppNotFoundError,
    ChannelNotAvailableError,
    NeedsClassicError,
    NotFoundError,
    NotInstalledError,
    OptionNotFoundError,
    RevisionNotAvailableError,
    _AlreadyInstalledError,
    _InterfacesUnchangedError,
    _NoUpdatesAvailableError,
)

from . import _state as state

if TYPE_CHECKING:
    from collections.abc import Iterable

    from charmlibs import snap


def _format_timestamp(dt: datetime.datetime) -> str:
    """Format a datetime the way ``charmlibs.snap._utils.parse_timestamp`` can read back.

    Always Z-suffixed with microseconds, which parses on both the Python 3.10 manual path and
    the ``fromisoformat`` path used from 3.11 onwards.
    """
    utc = dt.astimezone(datetime.timezone.utc) if dt.tzinfo is not None else dt
    return utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


class Api:
    """The mutable simulated snapd world, and the router dispatching onto it."""

    def __init__(
        self,
        installed: Iterable[state.Snap],
        *,
        store: Iterable[state.StoreSnap] | None,
        connections: Iterable[state.Connection],
        failures: Iterable[state.Failure],
    ) -> None:
        self.installed: dict[str, state.Snap] = {s.name: s for s in installed}
        self.store: dict[str, state.StoreSnap] | None = (
            None if store is None else {s.name: s for s in store}
        )
        self.connections: set[state.Connection] = set(connections)
        self.history: list[state.Operation] = []
        # Failures are matched in the order given; each tracks its own remaining budget.
        self._failures: list[tuple[state.Failure, int | None]] = [(f, f.times) for f in failures]

    # --- failure injection ---

    def _maybe_raise(self, action: str, snap_name: str | None) -> None:
        for i, (failure, remaining) in enumerate(self._failures):
            if failure.action not in (action, '*'):
                continue
            if failure.snap is not None and failure.snap != snap_name:
                continue
            if remaining == 0:
                continue
            if remaining is not None:
                self._failures[i] = (failure, remaining - 1)
            raise failure.error

    # --- entry points, matching charmlibs.snap._client's signatures ---

    def get(self, path: str, query: dict[str, Any] | None = None) -> object:
        if m := re.fullmatch(r'/v2/snaps/([^/]+)/conf', path):
            return self._config_get(m[1], query or {})
        if m := re.fullmatch(r'/v2/snaps/([^/]+)', path):
            return self._info(m[1])
        raise NotImplementedError(f'charmlibs-snap-testing does not model GET {path!r}')

    def get_logs(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self._logs(query or {})

    def post(self, path: str, body: dict[str, Any] | None = None) -> object:
        body = body or {}
        if m := re.fullmatch(r'/v2/snaps/([^/]+)', path):
            return self._snap_action(m[1], body)
        if path == '/v2/apps':
            return self._app_action(body)
        if path == '/v2/interfaces':
            return self._interface_action(body)
        if path == '/v2/aliases':
            return self._alias_action(body)
        raise NotImplementedError(f'charmlibs-snap-testing does not model POST {path!r}')

    def put(self, path: str, body: dict[str, Any] | None = None) -> object:
        if m := re.fullmatch(r'/v2/snaps/([^/]+)/conf', path):
            return self._config_set(m[1], body or {})
        raise NotImplementedError(f'charmlibs-snap-testing does not model PUT {path!r}')

    # --- /v2/snaps/{name} (GET) ---

    def _info(self, name: str) -> dict[str, Any]:
        installed = self.installed.get(name)
        if installed is None:
            raise NotFoundError(f'snap {name!r} is not installed', kind='snap-not-found', value='')
        result: dict[str, Any] = {
            'name': installed.name,
            'channel': installed.channel,
            'revision': installed.revision,
            'version': installed.version,
            'confinement': 'classic' if installed.classic else 'strict',
        }
        if installed.hold is not None:
            result['hold'] = _format_timestamp(installed.hold)
        return result

    # --- /v2/snaps/{name} (POST) ---

    def _snap_action(self, name: str, body: dict[str, Any]) -> object:
        action = body.get('action')
        if action == 'install':
            return self._install(name, body)
        if action == 'refresh':
            return self._refresh(name, body)
        if action == 'remove':
            return self._remove(name, body)
        if action == 'hold':
            return self._hold(name, body)
        if action == 'unhold':
            return self._unhold(name)
        raise NotImplementedError(
            f'charmlibs-snap-testing does not model action {action!r} on /v2/snaps/{{name}}'
        )

    def _install(self, name: str, body: dict[str, Any]) -> object:
        self._maybe_raise('install', name)
        if name in self.installed:
            raise _AlreadyInstalledError(
                f'snap {name!r} is already installed', kind='snap-already-installed', value=name
            )
        classic = bool(body.get('classic'))
        if self.store is not None:
            store_snap = self.store.get(name)
            if store_snap is None:
                raise NotFoundError(f'snap not found: {name!r}', kind='snap-not-found', value=name)
            if store_snap.classic and not classic:
                raise NeedsClassicError(
                    f'snap {name!r} requires classic confinement',
                    kind='snap-needs-classic',
                    value=name,
                )
            channel, revision = self._resolve_from_store(store_snap, body)
            version = store_snap.version
            services: dict[str, state.ServiceStatus] = {
                s: ('active' if s in store_snap.daemon_services else 'inactive')
                for s in store_snap.services
            }
        else:
            channel = _utils.normalize_channel(body.get('channel') or 'latest/stable')
            revision = str(body['revision']) if body.get('revision') else '1'
            version = '1.0'
            services = {}
        self.installed[name] = state.Snap(
            name,
            channel=channel,
            revision=revision,
            version=version,
            classic=classic,
            services=services,
        )
        self.history.append(
            state.Install(
                snap=name,
                channel=body.get('channel'),
                revision=str(body['revision']) if body.get('revision') else None,
                classic=classic,
            )
        )
        return {}

    def _resolve_from_store(
        self, store_snap: state.StoreSnap, body: dict[str, Any]
    ) -> tuple[str, str]:
        """Resolve (channel, revision) for an install/refresh against an authoritative store."""
        if body.get('revision'):
            revision = str(body['revision'])
            if revision not in {str(r) for r in store_snap.channels.values()}:
                raise RevisionNotAvailableError(
                    f'revision {revision} not available for snap {store_snap.name!r}',
                    kind='snap-revision-not-available',
                    value=revision,
                )
            return '', revision
        channel = _utils.normalize_channel(body.get('channel') or 'latest/stable')
        if channel not in store_snap.channels:
            raise ChannelNotAvailableError(
                f'no snap revision on channel {channel!r}',
                kind='snap-channel-not-available',
                value=channel,
            )
        return channel, str(store_snap.channels[channel])

    def _refresh(self, name: str, body: dict[str, Any]) -> object:
        self._maybe_raise('refresh', name)
        installed = self.installed.get(name)
        if installed is None:
            raise NotInstalledError(
                f'snap {name!r} is not installed', kind='snap-not-installed', value=name
            )
        if self.store is not None:
            store_snap = self.store.get(name)
            if store_snap is None:
                raise NotFoundError(f'snap not found: {name!r}', kind='snap-not-found', value=name)
            channel, revision = self._resolve_from_store(store_snap, body)
            channel = channel or installed.channel
            if revision == installed.revision:
                raise _NoUpdatesAvailableError(
                    f'snap {name!r} has no updates available',
                    kind='snap-no-update-available',
                    value='',
                )
            self.installed[name] = state.replace(installed, channel=channel, revision=revision)
        else:
            # Permissive mode: refreshes always find an update; only what the call named moves.
            channel = (
                _utils.normalize_channel(body['channel'])
                if body.get('channel')
                else installed.channel
            )
            revision = str(body['revision']) if body.get('revision') else installed.revision
            self.installed[name] = state.replace(installed, channel=channel, revision=revision)
        self.history.append(
            state.Refresh(
                snap=name,
                channel=body.get('channel'),
                revision=str(body['revision']) if body.get('revision') else None,
            )
        )
        return {}

    def _remove(self, name: str, body: dict[str, Any]) -> object:
        self._maybe_raise('remove', name)
        if name not in self.installed:
            raise NotInstalledError(
                f'snap {name!r} is not installed', kind='snap-not-installed', value=name
            )
        purge = bool(body.get('purge'))
        del self.installed[name]
        self.history.append(state.Remove(snap=name, purge=purge))
        return {}

    def _hold(self, name: str, body: dict[str, Any]) -> object:
        self._maybe_raise('hold', name)
        installed = self.installed.get(name)
        if installed is None:
            # The library pre-empts this with its own info() call; a direct caller still gets
            # the same error kind.
            raise NotFoundError(
                f'snap {name!r} is not installed', kind='snap-not-found', value=name
            )
        time_value = str(body.get('time', 'forever'))
        until = None if time_value == 'forever' else _utils.parse_timestamp(time_value)
        hold = datetime.datetime.max if until is None else until
        self.installed[name] = state.replace(installed, hold=hold)
        self.history.append(state.Hold(snap=name, until=until))
        return {}

    def _unhold(self, name: str) -> object:
        self._maybe_raise('unhold', name)
        installed = self.installed.get(name)
        if installed is not None:
            self.installed[name] = state.replace(installed, hold=None)
        self.history.append(state.Unhold(snap=name))
        return {}

    # --- /v2/snaps/{name}/conf ---

    def _config_get(self, name: str, query: dict[str, Any]) -> dict[str, Any]:
        self._maybe_raise('get', name)
        installed = self.installed.get(name)
        if installed is None:
            raise NotFoundError(
                f'snap {name!r} is not installed', kind='snap-not-found', value=name
            )
        keys_param = query.get('keys')
        keys = tuple(keys_param.split(',')) if keys_param else ()
        self.history.append(state.ConfigGet(snap=name, keys=keys))
        if not keys:
            return dict(installed.config)
        result: dict[str, Any] = {}
        for key in keys:
            if key not in installed.config:
                raise OptionNotFoundError(
                    f'snap {name!r} has no {key!r} configuration option',
                    kind='option-not-found',
                    value={'SnapName': name, 'Key': key},
                )
            result[key] = installed.config[key]
        return result

    def _config_set(self, name: str, body: dict[str, Any]) -> object:
        installed = self.installed.get(name)
        if installed is None:
            raise NotFoundError(
                f'snap {name!r} is not installed', kind='snap-not-found', value=name
            )
        sets = {k: v for k, v in body.items() if v is not None}
        unsets = tuple(k for k, v in body.items() if v is None)
        if sets:
            self._maybe_raise('set', name)
            config = dict(installed.config)
            config.update(sets)
            installed = state.replace(installed, config=config)
            self.installed[name] = installed
            self.history.append(state.ConfigSet(snap=name, values=sets))
        if unsets:
            self._maybe_raise('unset', name)
            config = dict(installed.config)
            for key in unsets:
                config.pop(key, None)
            installed = state.replace(installed, config=config)
            self.installed[name] = installed
            self.history.append(state.ConfigUnset(snap=name, keys=unsets))
        return {}

    # --- /v2/apps ---

    def _app_action(self, body: dict[str, Any]) -> object:
        action = body.get('action')
        if action not in ('start', 'stop', 'restart'):
            raise NotImplementedError(
                f'charmlibs-snap-testing does not model action {action!r} on /v2/apps'
            )
        names: list[str] = body.get('names', [])
        by_snap: dict[str, list[str | None]] = {}
        for entry in names:
            snap_name, _, service = entry.partition('.')
            by_snap.setdefault(snap_name, []).append(service or None)
        for snap_name, requested in by_snap.items():
            self._maybe_raise(action, snap_name)
            installed = self.installed.get(snap_name)
            if installed is None:
                raise AppNotFoundError(
                    f'snap {snap_name!r} not found', kind='app-not-found', value=snap_name
                )
            if requested == [None]:
                targeted = tuple(installed.services)
            else:
                targeted = tuple(s for s in requested if s is not None)
                for service in targeted:
                    if service not in installed.services:
                        raise AppNotFoundError(
                            f'snap {snap_name!r} has no service {service!r}',
                            kind='app-not-found',
                            value=snap_name,
                        )
            new_status: state.ServiceStatus = 'inactive' if action == 'stop' else 'active'
            services = dict(installed.services)
            for service in targeted:
                services[service] = new_status
            self.installed[snap_name] = state.replace(installed, services=services)
            if action == 'start':
                self.history.append(
                    state.Start(snap=snap_name, services=targeted, enable=bool(body.get('enable')))
                )
            elif action == 'stop':
                self.history.append(
                    state.Stop(
                        snap=snap_name,
                        services=targeted,
                        disable=bool(body.get('disable')),
                    )
                )
            else:
                self.history.append(state.Restart(snap=snap_name, services=targeted))
        return {}

    # --- /v2/logs ---

    def _logs(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        names_param = query.get('names', '')
        names = tuple(n for n in names_param.split(',') if n) if names_param else ()
        for name in names or (None,):
            self._maybe_raise('logs', name)
        if names:
            entries: list[snap.LogEntry] = []
            for name in names:
                installed = self.installed.get(name)
                if installed is None:
                    raise NotFoundError(
                        f'snap {name!r} is not installed', kind='snap-not-found', value=name
                    )
                entries.extend(installed.logs)
        else:
            entries = [e for s in sorted(self.installed) for e in self.installed[s].logs]
        self.history.append(state.Logs(snap=','.join(names), limit=query.get('n')))
        return [
            {
                'timestamp': _format_timestamp(e.timestamp),
                'sid': e.sid,
                'pid': str(e.pid),
                'message': e.message,
            }
            for e in entries
        ]

    # --- /v2/interfaces ---

    def _interface_action(self, body: dict[str, Any]) -> object:
        action = body.get('action')
        plug_entry = body['plugs'][0]
        slot_entry = body['slots'][0]
        plug = (plug_entry['snap'], plug_entry['plug'])
        slot = (slot_entry['snap'], slot_entry['slot'])
        connection = state.Connection(plug=plug, slot=slot)
        self._maybe_raise('connect' if action == 'connect' else 'disconnect', plug[0])
        if action == 'connect':
            if connection in self.connections:
                raise _InterfacesUnchangedError(
                    f'cannot connect {plug} to {slot}: already connected',
                    kind='interfaces-unchanged',
                    value='',
                )
            self.connections.add(connection)
            self.history.append(state.Connect(snap=plug[0], plug=plug, slot=slot))
        elif action == 'disconnect':
            if connection not in self.connections:
                raise _InterfacesUnchangedError(
                    f'cannot disconnect {plug} from {slot}: not connected',
                    kind='interfaces-unchanged',
                    value='',
                )
            self.connections.discard(connection)
            self.history.append(state.Disconnect(snap=plug[0], plug=plug, slot=slot))
        else:
            raise NotImplementedError(
                f'charmlibs-snap-testing does not model action {action!r} on /v2/interfaces'
            )
        return {}

    # --- /v2/aliases ---

    def _alias_action(self, body: dict[str, Any]) -> object:
        action = body.get('action')
        snap_name = body['snap']
        installed = self.installed.get(snap_name)
        if installed is None:
            raise NotFoundError(
                f'snap {snap_name!r} is not installed', kind='snap-not-found', value=snap_name
            )
        self._maybe_raise('alias' if action == 'alias' else 'unalias', snap_name)
        if action == 'alias':
            app = body['app']
            _, _, app_name = app.partition('.')
            app_name = app_name or app
            if app_name not in installed.services:
                raise AppNotFoundError(
                    f'snap {snap_name!r} has no service {app_name!r}',
                    kind='app-not-found',
                    value=snap_name,
                )
            alias = body['alias']
            aliases = dict(installed.aliases)
            aliases[alias] = app_name
            self.installed[snap_name] = state.replace(installed, aliases=aliases)
            self.history.append(state.Alias(snap=snap_name, app=app_name, alias=alias))
        elif action == 'unalias':
            alias = body.get('alias')
            aliases = dict(installed.aliases)
            if alias:
                aliases.pop(alias, None)
            else:
                aliases.clear()
            self.installed[snap_name] = state.replace(installed, aliases=aliases)
            self.history.append(state.Unalias(snap=snap_name, alias=alias))
        else:
            raise NotImplementedError(
                f'charmlibs-snap-testing does not model action {action!r} on /v2/aliases'
            )
        return {}
