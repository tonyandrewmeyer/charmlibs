# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from charmlibs.snap import _functions, _snapd_conf
from charmlibs.snap._errors import BadResponseError
from charmlibs.snap_testing import ConfigGet, ConfigSet, Snap, Snapd

_VITALITY_HINT = 'resilience.vitality-hint'


@dataclass
class MockConf:
    get_one: MagicMock
    set: MagicMock


@pytest.fixture
def mock_conf(monkeypatch: pytest.MonkeyPatch) -> MockConf:
    mocks = MockConf(get_one=MagicMock(), set=MagicMock())
    monkeypatch.setattr(_snapd_conf, 'get_one', mocks.get_one)
    monkeypatch.setattr(_snapd_conf, 'set', mocks.set)
    return mocks


class TestEnsureVitalityHint:
    def test_unset_adds_snap(self):
        with Snapd() as snapd:
            result = _functions.ensure_vitality_hint('foo')
        assert snapd.history == [
            ConfigGet(snap='system', keys=(_VITALITY_HINT,)),
            ConfigSet(snap='system', values={_VITALITY_HINT: 'foo'}),
        ]
        assert result is True

    def test_empty_string_adds_snap(self):
        # snapd stores '' when the option is set to an empty string.
        with Snapd([Snap('core', config={_VITALITY_HINT: ''})]) as snapd:
            result = _functions.ensure_vitality_hint('foo')
        assert snapd.installed['core'].config == {_VITALITY_HINT: 'foo'}
        assert result is True

    def test_appends_after_existing_snaps(self):
        with Snapd([Snap('core', config={_VITALITY_HINT: 'bar,baz'})]) as snapd:
            result = _functions.ensure_vitality_hint('foo')
        assert snapd.installed['core'].config == {_VITALITY_HINT: 'bar,baz,foo'}
        assert result is True

    @pytest.mark.parametrize('current', ['foo', 'foo,bar', 'bar,foo', 'bar,foo,baz'])
    def test_already_listed_is_no_op(self, current: str):
        with Snapd([Snap('core', config={_VITALITY_HINT: current})]) as snapd:
            result = _functions.ensure_vitality_hint('foo')
        assert snapd.history == [ConfigGet(snap='system', keys=(_VITALITY_HINT,))]
        assert snapd.installed['core'].config == {_VITALITY_HINT: current}
        assert result is False

    def test_instance_name_is_distinct_from_snap_name(self):
        with Snapd([Snap('core', config={_VITALITY_HINT: 'foo'})]) as snapd:
            result = _functions.ensure_vitality_hint('foo_bar')
        assert snapd.installed['core'].config == {_VITALITY_HINT: 'foo,foo_bar'}
        assert result is True

    @pytest.mark.parametrize('snap', ['', ' ', 'foo,bar', ' foo', 'foo '])
    def test_invalid_snap_name_raises_before_request(self, mock_conf: MockConf, snap: str):
        with pytest.raises(ValueError, match='snap name'):
            _functions.ensure_vitality_hint(snap)
        mock_conf.get_one.assert_not_called()
        mock_conf.set.assert_not_called()

    def test_non_string_value_raises_bad_response(self, mock_conf: MockConf):
        mock_conf.get_one.return_value = {'foo': 1}
        with pytest.raises(BadResponseError):
            _functions.ensure_vitality_hint('foo')
        mock_conf.set.assert_not_called()

    def test_snapd_raises_before_request(self, mock_conf: MockConf):
        with pytest.raises(ValueError, match='snapd'):
            _functions.ensure_vitality_hint('snapd')
        mock_conf.get_one.assert_not_called()
        mock_conf.set.assert_not_called()
