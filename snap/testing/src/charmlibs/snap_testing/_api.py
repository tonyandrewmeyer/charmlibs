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

Endpoint coverage matches design.md section 10. All six endpoint groups -- ``/v2/snaps/{name}``,
``/v2/snaps/{name}/conf``, ``/v2/apps``, ``/v2/interfaces``, ``/v2/aliases`` and ``/v2/logs`` --
are now exercised through ``charmlibs.snap``'s real public functions; see the implementation log
for what re-verifying conf/interfaces/aliases against those functions (rather than against the
fixtures and the standard snapd wire format alone, as before the fork sync) found.
"""

from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING, Any

from charmlibs.snap import _utils
from charmlibs.snap._errors import (
    APIError,
    AppNotFoundError,
    ChangeError,
    ChannelNotAvailableError,
    NeedsClassicError,
    NotInstalledError,
    OptionNotFoundError,
    RevisionNotAvailableError,
    _AlreadyInstalledError,
    _NotFoundError,
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
        # 'system'/'core' config is served whether or not a 'core' snap is installed (the conf
        # endpoints treat them as aliases for the same underlying config), so it needs storage
        # independent of `installed`. Only used when 'system'/'core' has no Snap entry of its own.
        self._system_config: dict[str, Any] = {}

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
            raise _NotFoundError(
                f'snap {name!r} is not installed', kind='snap-not-found', value=name
            )
        result: dict[str, Any] = {
            'name': installed.name,
            'channel': installed.channel,
            # snapd's 'tracking-channel' (the channel a refresh follows) is a distinct field
            # from 'channel' (where the installed revision came from) -- InstalledInfo.tracking
            # reads the former, and ensure_installed() depends on it to decide whether a
            # refresh is needed. Snap only models one channel, so the double reports the same
            # value for both, rather than leaving tracking-channel absent (which InstalledInfo
            # reads as '', silently defeating ensure_installed()'s already-on-channel check).
            'tracking-channel': installed.channel,
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
                raise _NotFoundError(
                    f'snap not found: {name!r}', kind='snap-not-found', value=name
                )
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
        self,
        store_snap: state.StoreSnap,
        body: dict[str, Any],
        default_channel: str = 'latest/stable',
    ) -> tuple[str, str]:
        """Resolve (channel, revision) for an install/refresh against an authoritative store.

        ``default_channel`` is what an unspecified channel means for this request. An install
        with no channel comes from ``latest/stable``; a *refresh* with no channel follows the
        snap's tracked channel instead -- confirmed against real snapd 2.76
        (IMPLEMENTATION.md 2026-09-06, candidate 1(a)), where ``juju`` tracking ``3/stable``
        with no ``latest/stable`` at all is correctly reported as having no update.
        """
        if body.get('revision'):
            revision = str(body['revision'])
            if revision not in {str(r) for r in store_snap.channels.values()}:
                raise RevisionNotAvailableError(
                    f'revision {revision} not available for snap {store_snap.name!r}',
                    kind='snap-revision-not-available',
                    value=revision,
                )
            return '', revision
        channel = _utils.normalize_channel(body.get('channel') or default_channel)
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
            # snapd's own response here carries no 'kind' at all: refresh() can't tell "not
            # installed" from "installed but the store dropped it" from this alone, and probes
            # /v2/snaps/{name} (our _info) to disambiguate. See test_snapd_snaps.py's
            # TestRefreshNotInstalled and the functional
            # test_raw_refresh_not_installed_has_no_kind.
            raise APIError(
                f'cannot refresh {name!r}: snap {name!r} is not installed', kind='', value=''
            )
        if self.store is not None:
            store_snap = self.store.get(name)
            if store_snap is None:
                raise _NotFoundError(
                    f'snap not found: {name!r}', kind='snap-not-found', value=name
                )
            channel, revision = self._resolve_from_store(
                store_snap, body, default_channel=installed.channel
            )
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
            # As for refresh, snapd's response here carries no 'kind': hold() probes
            # /v2/snaps/{name} (our _info) on failure to get a typed error. See
            # test_snapd_snaps.py's TestHold.test_hold_not_installed and the functional
            # test_raw_hold_not_installed_has_no_kind.
            raise APIError(
                f'cannot hold {name!r}: snap {name!r} is not installed', kind='', value=''
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
        # A bare conf GET can't distinguish an absent snap from an installed one with no
        # configuration -- snapd answers both with an empty dict -- so this never raises for a
        # missing snap. get() disambiguates itself, by probing /v2/snaps/{name} (our _info) when
        # the result is empty. A specific missing key raises option-not-found either way, since
        # snapd can't tell "unset key" from "no such snap" apart at this endpoint either.
        self._maybe_raise('get', name)
        config = self._config_store(name)
        keys_param = query.get('keys')
        keys = tuple(keys_param.split(',')) if keys_param else ()
        self.history.append(state.ConfigGet(snap=name, keys=keys))
        if not keys:
            return dict(config)
        result: dict[str, Any] = {}
        for key in keys:
            if key not in config:
                raise OptionNotFoundError(
                    f'snap {name!r} has no {key!r} configuration option',
                    kind='option-not-found',
                    value={'SnapName': name, 'Key': key},
                )
            result[key] = config[key]
        return result

    def _config_set(self, name: str, body: dict[str, Any]) -> object:
        # snap-not-found is returned for a missing snap, but never for 'system'/'core': their
        # configuration is served whether or not the core snap is installed.
        if name not in ('system', 'core') and name not in self.installed:
            raise _NotFoundError(
                f'snap {name!r} is not installed', kind='snap-not-found', value=name
            )
        sets = {k: v for k, v in body.items() if v is not None}
        unsets = tuple(k for k, v in body.items() if v is None)
        if sets:
            self._maybe_raise('set', name)
            config = dict(self._config_store(name))
            config.update(sets)
            self._store_config(name, config)
            self.history.append(state.ConfigSet(snap=name, values=sets))
        if unsets:
            self._maybe_raise('unset', name)
            config = dict(self._config_store(name))
            for key in unsets:
                config.pop(key, None)
            self._store_config(name, config)
            self.history.append(state.ConfigUnset(snap=name, keys=unsets))
        return {}

    def _config_store(self, name: str) -> dict[str, Any]:
        installed = self.installed.get(name)
        if installed is not None:
            return dict(installed.config)
        if name in ('system', 'core'):
            return dict(self._system_config)
        return {}

    def _store_config(self, name: str, config: dict[str, Any]) -> None:
        installed = self.installed.get(name)
        if installed is not None:
            self.installed[name] = state.replace(installed, config=config)
        elif name in ('system', 'core'):
            self._system_config = config

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
                # snapd distinguishes the two request forms for a snap it does not have, and
                # answers the snap-alone form without needing a probe -- confirmed against real
                # snapd 2.76 (IMPLEMENTATION.md 2026-09-06, candidate 2):
                #   names=[snap]      404 snap-not-found  snap "x" not found
                #   names=[snap.svc]  404 app-not-found   snap "x" has no service "svc"
                if requested == [None]:
                    raise _NotFoundError(
                        f'snap "{snap_name}" not found', kind='snap-not-found', value=snap_name
                    )
                service = next(s for s in requested if s is not None)
                raise AppNotFoundError(
                    f'snap "{snap_name}" has no service "{service}"',
                    kind='app-not-found',
                    value=snap_name,
                )
            if requested == [None]:
                if not installed.services:
                    # snapd answers app-not-found for a whole-snap action when the snap has no
                    # services at all, not just for a named service it lacks -- confirmed by the
                    # functional test_{start,stop,restart}_snap_with_no_services_raises.
                    raise AppNotFoundError(
                        f'snap "{snap_name}" has no services',
                        kind='app-not-found',
                        value=snap_name,
                    )
                targeted = tuple(installed.services)
            else:
                targeted = tuple(s for s in requested if s is not None)
                for service in targeted:
                    if service not in installed.services:
                        raise AppNotFoundError(
                            f'snap "{snap_name}" has no service "{service}"',
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
                    raise _NotFoundError(
                        f'snap {name!r} is not installed', kind='snap-not-found', value=name
                    )
                if not installed.services:
                    # snapd answers app-not-found for a snap with no services at all when its
                    # logs are queried by name -- confirmed by the functional
                    # test_logs_snap_with_no_services_raises, the same shape as /v2/apps's
                    # whole-snap action on a service-less snap (see _app_action above).
                    raise AppNotFoundError(
                        f'snap "{name}" has no services', kind='app-not-found', value=name
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
        if action not in ('connect', 'disconnect'):
            raise NotImplementedError(
                f'charmlibs-snap-testing does not model action {action!r} on /v2/interfaces'
            )
        plug_entry = body['plugs'][0]
        slot_entry = body['slots'][0]
        plug = (plug_entry['snap'], plug_entry['plug'])
        slot = (slot_entry['snap'], slot_entry['slot'])
        self._maybe_raise(action, plug[0])
        # An empty *plug* side is rejected outright; only an empty *slot* side auto-resolves to
        # the system snap. Both checks run before either side's not-installed check, and the
        # plug snap is checked before the plug name -- confirmed against real snapd 2.76
        # (IMPLEMENTATION.md 2026-09-06, candidate 5), which answers 400 with no kind and:
        #   plugs=[{snap:'',  plug:_}]  cannot resolve connection, plug snap name is empty
        #   plugs=[{snap:_,   plug:''}] cannot resolve connection, plug name is empty
        if action == 'connect':
            if not plug[0]:
                raise APIError(
                    'cannot resolve connection, plug snap name is empty', kind='', value=''
                )
            if not plug[1]:
                raise APIError('cannot resolve connection, plug name is empty', kind='', value='')
        # snapd's response for a plug/slot snap that isn't installed carries no 'kind' either;
        # connect()/disconnect() probe /v2/snaps/{name} (our _info) to get a typed error. An
        # empty slot side is 'auto-resolve to the system snap', never a snap to check.
        for snap_name in (plug[0], slot[0]):
            if snap_name and snap_name not in self.installed:
                raise APIError(f'snap {snap_name!r} is not installed', kind='', value='')
        if action == 'connect':
            # Connecting an already-connected plug/slot succeeds silently -- snapd's connect
            # endpoint is idempotent, unlike disconnect (see
            # test_connect_already_connected_no_error in the functional suite). Never raises
            # interfaces-unchanged.
            self.connections.add(state.Connection(plug=plug, slot=slot))
            self.history.append(state.Connect(snap=plug[0], plug=plug, slot=slot))
            return {}
        # disconnect: a fully-specified (two-sided) disconnect of a pair that isn't connected
        # raises (a plain 'not connected' APIError, not interfaces-unchanged). A one-sided
        # disconnect (only plug or only slot named) that matches nothing is a no-op -- snapd
        # sends interfaces-unchanged there, which the library suppresses, so our double just
        # doesn't raise. See TestDisconnect in the functional suite.
        two_sided = all(plug) and all(slot)
        matched = {
            c
            for c in self.connections
            if (not any(plug) or c.plug == plug) and (not any(slot) or c.slot == slot)
        }
        if two_sided and not matched:
            raise APIError(f'{plug} and {slot} are not connected', kind='', value='')
        self.connections -= matched
        for connection in matched:
            self.history.append(
                state.Disconnect(
                    snap=connection.plug[0], plug=connection.plug, slot=connection.slot
                )
            )
        return {}

    # --- /v2/aliases ---

    def _alias_action(self, body: dict[str, Any]) -> object:
        action = body.get('action')
        if action == 'alias':
            return self._alias(body)
        if action == 'unalias':
            return self._unalias(body)
        raise NotImplementedError(
            f'charmlibs-snap-testing does not model action {action!r} on /v2/aliases'
        )

    def _alias(self, body: dict[str, Any]) -> object:
        snap_name = body['snap']
        self._maybe_raise('alias', snap_name)
        installed = self.installed.get(snap_name)
        if installed is None:
            # Unlike most endpoints, snapd sends the unambiguous 'snap-not-installed' kind here
            # (also used by remove), so alias() needs no narrowing of its own -- the client
            # already maps it straight to NotInstalledError. See
            # test_alias_not_installed_snap_raises in the functional suite.
            raise NotInstalledError(
                f'snap {snap_name!r} is not installed', kind='snap-not-installed', value=snap_name
            )
        alias = body['alias']
        app = body['app']
        _, _, app_name = app.partition('.')
        app_name = app_name or app
        # An alias name already claimed by a different installed snap conflicts, and so does one
        # that collides with any installed snap's own command namespace (its bare name). Both
        # are async change failures, not synchronous validation -- see
        # test_alias_duplicate_name_different_snap_raises and
        # test_alias_name_conflicts_with_snap_command_namespace in the functional suite.
        if alias in self.installed:
            raise ChangeError(
                f'alias {alias!r} conflicts with the command'
                f' namespace of installed snap {alias!r}',
                kind='charmlibs-snap-change-error',
                value='',
                status='Error',
            )
        for other_name, other in self.installed.items():
            if other_name != snap_name and alias in other.aliases:
                raise ChangeError(
                    f'cannot enable alias {alias!r} for {snap_name!r},'
                    f' already enabled for {other_name!r}',
                    kind='charmlibs-snap-change-error',
                    value='',
                    status='Error',
                )
        if app_name not in installed.services:
            # Aliasing a nonexistent app also fails as an async change, not a synchronous
            # app-not-found -- see test_alias_nonexistent_app_raises_snap_change_error.
            raise ChangeError(
                f'cannot enable alias {alias!r} for {snap_name!r}: no such app {app_name!r}',
                kind='charmlibs-snap-change-error',
                value='',
                status='Error',
            )
        aliases = dict(installed.aliases)
        aliases[alias] = app_name
        self.installed[snap_name] = state.replace(installed, aliases=aliases)
        self.history.append(state.Alias(snap=snap_name, app=app_name, alias=alias))
        return {}

    def _unalias(self, body: dict[str, Any]) -> object:
        # unalias's request has no 'snap' field -- it names the alias only, snapd-wide -- so the
        # double has to search for which installed snap (if any) owns it.
        alias = body['alias']
        owner = next((name for name, s in self.installed.items() if alias in s.aliases), None)
        self._maybe_raise('unalias', owner)
        if owner is None:
            # A base, kindless Error -- see test_unalias_nonexistent_alias_raises.
            raise APIError(f'cannot find alias {alias!r}', kind='', value='')
        installed = self.installed[owner]
        aliases = dict(installed.aliases)
        del aliases[alias]
        self.installed[owner] = state.replace(installed, aliases=aliases)
        self.history.append(state.Unalias(snap=owner, alias=alias))
        return {}
