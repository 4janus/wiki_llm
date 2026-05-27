"""Tests for advisor_app: imports, signature, and _sort_advisors."""
from __future__ import annotations
import inspect
from src.ui.advisor_app import _ADVISOR_ORDER, _sort_advisors, start_advisor_ui


def test_start_advisor_ui_is_callable():
    assert callable(start_advisor_ui)


def test_start_advisor_ui_signature():
    sig = inspect.signature(start_advisor_ui)
    params = list(sig.parameters.keys())
    assert "root" in params
    assert "llm_config" in params
    assert "port" in params
    assert "host" in params


def test_advisor_order_has_20_entries():
    assert len(_ADVISOR_ORDER) == 20


def test_sort_advisors_preserves_known_order():
    """Advisors in _ADVISOR_ORDER come out in that order."""
    mock = {slug: object() for slug in reversed(_ADVISOR_ORDER)}
    result = _sort_advisors(mock)
    assert list(result.keys()) == _ADVISOR_ORDER


def test_sort_advisors_unknown_slugs_appended_alphabetically():
    """Advisors not in _ADVISOR_ORDER are appended after known ones."""
    mock = {"zebra": object(), "apple": object(), "testamente": object()}
    result = _sort_advisors(mock)
    keys = list(result.keys())
    assert keys[0] == "testamente"
    assert keys[1:] == ["apple", "zebra"]


def test_sort_advisors_empty_input():
    assert _sort_advisors({}) == {}


def test_sort_advisors_returns_new_dict():
    """Does not mutate the input dict."""
    original = {"testamente": object()}
    result = _sort_advisors(original)
    assert result is not original
