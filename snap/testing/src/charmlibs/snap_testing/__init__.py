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

"""A stateful fake snapd for testing charms that use :mod:`charmlibs.snap`.

Use :class:`Snapd` as a context manager around charm execution (``ops.testing.Context.run()``,
``Harness``, or plain function calls) to make the real ``charmlibs.snap`` functions work without
a real snapd: install/refresh/remove, service start/stop/restart, config, interfaces, aliases,
and log retrieval all run against an in-memory model instead of a unix socket.

A ``snapd`` pytest fixture is available automatically via the ``pytest11`` entry point for the
zero-config case.
"""

from ._consistency import SnapStateValidationError
from ._snapd import Snapd
from ._state import (
    Alias,
    ConfigGet,
    ConfigSet,
    ConfigUnset,
    Connect,
    Connection,
    Disconnect,
    Failure,
    Hold,
    Install,
    Logs,
    Operation,
    Refresh,
    Remove,
    Restart,
    ServiceStatus,
    Snap,
    Start,
    Stop,
    StoreSnap,
    Unalias,
    Unhold,
)
from ._version import __version__ as __version__

__all__ = [
    'Alias',
    'ConfigGet',
    'ConfigSet',
    'ConfigUnset',
    'Connect',
    'Connection',
    'Disconnect',
    'Failure',
    'Hold',
    'Install',
    'Logs',
    'Operation',
    'Refresh',
    'Remove',
    'Restart',
    'ServiceStatus',
    'Snap',
    'SnapStateValidationError',
    'Snapd',
    'Start',
    'Stop',
    'StoreSnap',
    'Unalias',
    'Unhold',
]
