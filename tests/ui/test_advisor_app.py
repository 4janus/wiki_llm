"""Smoke tests for advisor_app imports and start_advisor_ui signature."""
from __future__ import annotations
import inspect
from src.ui.advisor_app import start_advisor_ui


def test_start_advisor_ui_is_callable():
    assert callable(start_advisor_ui)


def test_start_advisor_ui_signature():
    sig = inspect.signature(start_advisor_ui)
    params = list(sig.parameters.keys())
    assert "root" in params
    assert "llm_config" in params
    assert "port" in params
    assert "host" in params
