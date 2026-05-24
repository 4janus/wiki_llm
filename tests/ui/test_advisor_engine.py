"""Tests for AdvisorEngine discovery and config parsing."""
from __future__ import annotations
import tempfile
from pathlib import Path

import pytest

from src.ui.advisor_engine import (
    AdvisorEngine,
    AdvisorConfig,
    ServiceConfig,
    _parse_frontmatter,
    _make_chat_cfg,
)


# --- _parse_frontmatter ---

def test_parse_frontmatter_valid():
    content = "---\nservice_id: 1\ntitle: Test\ncategory: Kom i gang\n---\n\nBody text here."
    fm, body = _parse_frontmatter(content)
    assert fm["service_id"] == "1"
    assert fm["title"] == "Test"
    assert fm["category"] == "Kom i gang"
    assert "Body text here." in body


def test_parse_frontmatter_no_frontmatter():
    content = "Just body text."
    fm, body = _parse_frontmatter(content)
    assert fm == {}
    assert body == "Just body text."


# --- _make_chat_cfg ---

def test_make_chat_cfg_readable():
    cfg = _make_chat_cfg("TestWiki", Path("/tmp"), "System prompt text")
    assert cfg.wiki_name == "TestWiki"
    assert cfg.wiki_dir == Path("/tmp")
    assert cfg.prompt_chat.read_text() == "System prompt text"
    assert cfg.prompt_chat.read_text(encoding="utf-8") == "System prompt text"


# --- AdvisorEngine.discover ---

def _make_advisor_dir(tmp: Path, advisor_id: str, title: str, n_services: int = 2) -> None:
    d = tmp / advisor_id
    d.mkdir()
    (d / "index.md").write_text(f"# {title}\n\nBeskrivelse.", encoding="utf-8")
    p = d / "prompts"
    p.mkdir()
    for i in range(1, n_services + 1):
        (p / f"{i:02d}-service-{i}.md").write_text(
            f"---\nservice_id: {i}\ntitle: Service {i}\ncategory: Kategori\n---\n\nPrompt {i}.",
            encoding="utf-8",
        )


def test_discover_single_advisor():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_advisor_dir(root, "testamente", "Testamente")
        engine = AdvisorEngine(root=root, llm=None)
        advisors = engine.discover()
        assert "testamente" in advisors
        adv = advisors["testamente"]
        assert adv.title == "Testamente"
        assert len(adv.services) == 2
        assert adv.services[0].id == 1
        assert adv.services[0].title == "Service 1"
        assert adv.services[0].category == "Kategori"
        assert "Prompt 1." in adv.services[0].prompt


def test_discover_ignores_dirs_without_prompts():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_advisor_dir(root, "testamente", "Testamente")
        (root / "empty-dir").mkdir()
        engine = AdvisorEngine(root=root, llm=None)
        advisors = engine.discover()
        assert "testamente" in advisors
        assert "empty-dir" not in advisors


def test_discover_title_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = root / "boligkob"
        d.mkdir()
        p = d / "prompts"
        p.mkdir()
        (p / "01-x.md").write_text(
            "---\nservice_id: 1\ntitle: X\ncategory: A\n---\nPrompt.",
            encoding="utf-8",
        )
        engine = AdvisorEngine(root=root, llm=None)
        advisors = engine.discover()
        assert advisors["boligkob"].title == "Boligkob"


def test_discover_caches_result():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_advisor_dir(root, "testamente", "Testamente")
        engine = AdvisorEngine(root=root, llm=None)
        r1 = engine.discover()
        r2 = engine.discover()
        assert r1 is r2


def test_get_history_empty_for_unknown_key():
    engine = AdvisorEngine(root=Path("."), llm=None)
    assert engine.get_history("testamente", 1) == []


# --- Error handling ---

def test_get_engine_unknown_advisor_raises():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_advisor_dir(root, "testamente", "Testamente")
        engine = AdvisorEngine(root=root, llm=None)
        with pytest.raises(KeyError, match="Unknown advisor"):
            engine.get_engine("nonexistent", 1)


def test_get_engine_unknown_service_raises():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_advisor_dir(root, "testamente", "Testamente", n_services=2)
        engine = AdvisorEngine(root=root, llm=None)
        with pytest.raises(KeyError, match="Service 99 not found"):
            engine.get_engine("testamente", 99)


import asyncio


def test_ask_without_llm_raises():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_advisor_dir(root, "testamente", "Testamente")
        engine = AdvisorEngine(root=root, llm=None)
        with pytest.raises(RuntimeError, match="LLM client"):
            asyncio.run(engine.ask("testamente", 1, "test question"))
