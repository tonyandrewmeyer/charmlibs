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

"""``Snapd``: the simulated snapd, entered as a context manager around charm execution."""

from __future__ import annotations

from typing import TYPE_CHECKING

from charmlibs.snap import _client

from . import _api, _consistency
from . import _state as state

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

_PATCHED_FUNCTIONS = ('get', 'get_logs', 'post', 'put')


class Snapd:
    """A simulated snapd, for use as a context manager around charm execution.

    Entering patches ``charmlibs.snap._client.get``, ``.get_logs``, ``.post`` and ``.put``;
    exiting restores them. A ``Snapd`` instance is single-use, like ``ops.testing.Context``: it
    cannot be re-entered once used, so a test can't accidentally accumulate state across runs.
    """

    def __init__(
        self,
        installed: Iterable[state.Snap] = (),
        *,
        store: Iterable[state.StoreSnap] | None = None,
        connections: Iterable[state.Connection] = (),
        failures: Iterable[state.Failure] = (),
    ) -> None:
        installed = tuple(installed)
        store_tuple = None if store is None else tuple(store)
        connections = tuple(connections)
        failures = tuple(failures)
        _consistency.validate_world(
            installed=installed,
            store=store_tuple,
            connections=connections,
            failures=failures,
        )
        self._api = _api.Api(
            installed, store=store_tuple, connections=connections, failures=failures
        )
        self._used = False
        self._patched: list[tuple[object, str, object]] = []

    @property
    def installed(self) -> Mapping[str, state.Snap]:
        """The snaps installed on the simulated machine, keyed by name.

        Rebuilt as the charm acts. This is the analogue of Scenario's ``state_out``.
        """
        return dict(self._api.installed)

    @property
    def connections(self) -> frozenset[state.Connection]:
        """Currently connected plug/slot pairs."""
        return frozenset(self._api.connections)

    @property
    def history(self) -> Sequence[state.Operation]:
        """Every operation the charm performed, in order.

        The analogue of ``Context.juju_log`` -- it records the path taken, not just the
        destination. Only operations that completed without raising are recorded.
        """
        return list(self._api.history)

    def __enter__(self) -> Snapd:
        if self._used:
            raise RuntimeError('a Snapd instance is single-use; construct a new one per test')
        self._used = True
        for name in _PATCHED_FUNCTIONS:
            self._patched.append((_client, name, getattr(_client, name)))
            setattr(_client, name, getattr(self._api, name))
        return self

    def __exit__(self, *exc_info: object) -> None:
        for target, name, original in reversed(self._patched):
            setattr(target, name, original)
        self._patched.clear()
