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

import contextlib
from typing import TYPE_CHECKING

from charmlibs.snap import _client

from . import _api, _consistency
from . import _state as state

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping, Sequence

_PATCHED_FUNCTIONS = ('get', 'get_logs', 'post', 'put')

# The Snapd instances whose outermost scope is open, innermost last.
_open: list[Snapd] = []


class Snapd:
    """A simulated snapd, for use as a context manager around charm execution.

    Entering patches ``charmlibs.snap._client.get``, ``.get_logs``, ``.post`` and ``.put``;
    exiting the outermost scope restores them. A ``Snapd`` is reentrant, so a fixture and the
    test that uses it can each open it. It is single-use, though: entering it again after its
    outermost scope has exited raises ``RuntimeError``, so a test can't accidentally carry
    state from one run into the next.

    ``architecture`` is what :func:`charmlibs.snap.system_info` reports. It defaults to
    ``'amd64'``, so a charm that picks something per architecture gets the same answer on every
    machine its tests run on.
    """

    def __init__(
        self,
        installed: Iterable[state.Snap] = (),
        *,
        store: Iterable[state.StoreSnap] | None = None,
        connections: Iterable[state.Connection] = (),
        failures: Iterable[state.Failure] = (),
        architecture: str = 'amd64',
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
            architecture=architecture,
        )
        self._api: _api.Api | _api.StatelessApi = _api.Api(
            installed,
            store=store_tuple,
            connections=connections,
            failures=failures,
            architecture=architecture,
        )
        self._used = False
        self._depth = 0
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

        The analogue of ``Context.juju_log``: it records the path taken, not just the
        destination. Only operations that completed without raising are recorded.
        """
        return list(self._api.history)

    def __enter__(self) -> Snapd:
        if self._depth:
            self._depth += 1
            return self
        if self._used:
            raise RuntimeError('a Snapd instance is single-use; construct a new one per test')
        self._used = True
        self._depth = 1
        _open.append(self)
        for name in _PATCHED_FUNCTIONS:
            self._patched.append((_client, name, getattr(_client, name)))
            setattr(_client, name, getattr(self._api, name))
        return self

    def __exit__(self, *exc_info: object) -> None:
        self._depth -= 1
        if self._depth:
            return
        _open.remove(self)
        for target, name, original in reversed(self._patched):
            setattr(target, name, original)
        self._patched.clear()


class _StatelessSnapd(Snapd):
    """The ``Snapd`` a ``mocked()`` with no ``Snapd`` open yields, which keeps no state.

    Its ``installed``, ``connections`` and ``history`` are always empty, because nothing is kept
    to report.
    """

    def __init__(self) -> None:
        super().__init__()
        self._api = _api.StatelessApi()


@contextlib.contextmanager
def mocked() -> Iterator[Snapd]:
    """Mock out snapd for the length of the ``with`` block.

    If a :class:`Snapd` is already open, this joins it and does nothing else, so the code under
    test talks to the test's ``Snapd``.

    If no ``Snapd`` is open, this keeps no state at all. Every snap counts as installed on
    ``latest/stable``, at revision ``'1'`` and version ``'1.0'``, which are the defaults for a
    :class:`Snap`. Every service exists, and every operation succeeds. Reads see a snap with no
    configuration, whatever the code under test has set. The library's own argument checks still
    run, so an invalid snap name still raises ``ValueError``. The ``Snapd`` returned has nothing in
    its ``installed``, ``connections`` or ``history``, because nothing is kept.

    A ``mocked()`` inside another one joins the outer one. A ``Snapd`` opened inside a
    ``mocked()`` with no ``Snapd`` open takes over until it's closed, and a ``mocked()`` opened
    inside it joins it.

    This is the reentrant, argument-free ``mocked()`` that every charmlibs testing package
    provides, so a test harness can open it around each dispatch. Since a ``mocked()`` on its own
    keeps nothing, it makes no difference whether it's opened once per dispatch or once for a
    whole test. For strict behaviour, a starting state, a store, injected failures, or anything to
    check afterwards, open a ``Snapd`` around the whole test instead.
    """
    with _open[-1] if _open else _StatelessSnapd() as snapd:
        yield snapd
