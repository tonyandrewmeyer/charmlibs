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

"""The ``snapd`` pytest fixture, registered via the ``pytest11`` entry point."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ._snapd import Snapd

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def snapd() -> Iterator[Snapd]:
    """A zero-config, permissive-mode :class:`Snapd`, entered for the duration of the test."""
    with Snapd() as s:
        yield s
