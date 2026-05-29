"""Tests for the FastAPI rewrite of advisor_app."""
from __future__ import annotations

import inspect
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from src.ui.advisor_app import _ADVISOR_ORDER, _create_app, _sort_advisors, start_advisor_ui
from src.ui.advisor_engine import AdvisorConfig, ServiceConfig

TESTAMENTE = AdvisorConfig(
    id="testamente",
    title="Testamente",
    services=[
        ServiceConfig(id=1, title="Opret testamente", category="Oprettelse", prompt="du er juridisk rådgiver"),
        ServiceConfig(id=2, title="Ændre testamente", category="Ændring", prompt="du hjælper med ændringer"),
    ],
    wiki_dir=Path("/fake/testamente"),
)

AEGTEPAGT = AdvisorConfig(
    id="aegtepagt",
    title="Ægtepagt",
    services=[
        ServiceConfig(id=1, title="Opret ægtepagt", category="Oprettelse", prompt="du er specialist"),
    ],
    wiki_dir=Path("/fake/aegtepagt"),
)


def _make_engine(advisors: dict | None = None) -> MagicMock:
    engine = MagicMock()
    engine.discover.return_value = advisors if advisors is not None else {"testamente": TESTAMENTE}
    engine.ask = AsyncMock(return_value="Et testamente er et juridisk dokument.")
    engine.get_history.return_value = []
    engine.clear.return_value = None
    return engine


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    app = _create_app(tmp_path, MagicMock(), _engine=_make_engine())
    return TestClient(app)


# ── Signature tests (must survive the rewrite) ─────────────────

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
    mock = {slug: object() for slug in reversed(_ADVISOR_ORDER)}
    result = _sort_advisors(mock)
    assert list(result.keys()) == _ADVISOR_ORDER


def test_sort_advisors_unknown_slugs_appended_alphabetically():
    mock = {"zebra": object(), "apple": object(), "testamente": object()}
    result = _sort_advisors(mock)
    keys = list(result.keys())
    assert keys[0] == "testamente"
    assert keys[1:] == ["apple", "zebra"]


# ── /api/advisors ──────────────────────────────────────────────

def test_api_advisors_returns_list(client: TestClient):
    resp = client.get("/api/advisors")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "testamente"
    assert data[0]["title"] == "Testamente"


def test_api_advisors_service_shape(client: TestClient):
    data = client.get("/api/advisors").json()
    svc = data[0]["services"][0]
    assert svc["id"] == 1
    assert svc["title"] == "Opret testamente"
    assert svc["category"] == "Oprettelse"


def test_api_advisors_sorted(tmp_path: Path):
    engine = _make_engine({"aegtepagt": AEGTEPAGT, "testamente": TESTAMENTE})
    app = _create_app(tmp_path, MagicMock(), _engine=engine)
    client = TestClient(app)
    data = client.get("/api/advisors").json()
    ids = [a["id"] for a in data]
    assert ids.index("testamente") < ids.index("aegtepagt")


def test_create_app_raises_when_no_advisors(tmp_path: Path):
    engine = _make_engine({})
    with pytest.raises(RuntimeError, match="Ingen rådgivere"):
        _create_app(tmp_path, MagicMock(), _engine=engine)


# ── /api/chat SSE ──────────────────────────────────────────────

def test_api_chat_returns_event_stream(client: TestClient):
    resp = client.post("/api/chat", json={
        "advisor_id": "testamente",
        "service_id": 1,
        "question": "Hvad er et testamente?",
        "docs": [],
        "session_id": "test-session",
    })
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]


def test_api_chat_sse_format(client: TestClient):
    resp = client.post("/api/chat", json={
        "advisor_id": "testamente",
        "service_id": 1,
        "question": "test",
        "docs": [],
        "session_id": "s1",
    })
    lines = [l for l in resp.text.split("\n") if l.startswith("data: ")]
    assert lines[-1] == "data: [DONE]"
    for line in lines[:-1]:
        payload = json.loads(line[6:])
        assert "t" in payload
        assert isinstance(payload["t"], str)


def test_api_chat_reassembled_answer(client: TestClient):
    resp = client.post("/api/chat", json={
        "advisor_id": "testamente",
        "service_id": 1,
        "question": "test",
        "docs": [],
        "session_id": "s2",
    })
    lines = [l for l in resp.text.split("\n") if l.startswith("data: ") and l != "data: [DONE]"]
    tokens = [json.loads(l[6:])["t"] for l in lines]
    reassembled = "".join(tokens)
    assert reassembled == "Et testamente er et juridisk dokument."


def test_api_chat_prepends_docs(tmp_path: Path):
    engine = _make_engine()
    app = _create_app(tmp_path, MagicMock(), _engine=engine)
    client = TestClient(app)
    client.post("/api/chat", json={
        "advisor_id": "testamente",
        "service_id": 1,
        "question": "Er dette gyldigt?",
        "docs": [{"name": "kontrakt.pdf", "text": "§1 Parterne aftaler..."}],
        "session_id": "s3",
    })
    call_args = engine.ask.call_args[0]
    assert "kontrakt.pdf" in call_args[2]
    assert "Er dette gyldigt?" in call_args[2]


# ── DELETE /api/history ────────────────────────────────────────

def test_delete_history_returns_204(client: TestClient):
    resp = client.delete("/api/history/testamente/1")
    assert resp.status_code == 204


def test_delete_history_calls_engine_clear(tmp_path: Path):
    engine = _make_engine()
    app = _create_app(tmp_path, MagicMock(), _engine=engine)
    client = TestClient(app)
    client.delete("/api/history/testamente/1")
    engine.clear.assert_called_once_with("testamente", 1)


# ── POST /api/upload ───────────────────────────────────────────

def test_upload_returns_name_and_text(client: TestClient):
    content = b"This is a plain text document."
    resp = client.post(
        "/api/upload",
        files={"file": ("note.txt", content, "text/plain")},
        data={"session_id": "s1"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "note.txt"
    assert isinstance(data["text"], str)
    assert len(data["text"]) > 0


def test_upload_graceful_error_on_unparseable(client: TestClient):
    resp = client.post(
        "/api/upload",
        files={"file": ("corrupt.pdf", b"\x00\x01\x02", "application/pdf")},
        data={"session_id": "s1"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "corrupt.pdf"
    assert isinstance(data["text"], str)


# ── GET /api/download ──────────────────────────────────────────

def test_download_md_contains_history(tmp_path: Path):
    engine = _make_engine()
    engine.get_history.return_value = [
        {"role": "user", "content": "Hvad koster det?"},
        {"role": "assistant", "content": "Det koster kr 200."},
    ]
    app = _create_app(tmp_path, MagicMock(), _engine=engine)
    client = TestClient(app)
    resp = client.get("/api/download/testamente/1")
    assert resp.status_code == 200
    assert "attachment" in resp.headers["content-disposition"]
    assert "Hvad koster det?" in resp.text
    assert "Det koster kr 200." in resp.text


def test_download_md_default_format(tmp_path: Path):
    engine = _make_engine()
    engine.get_history.return_value = [{"role": "user", "content": "test"}]
    app = _create_app(tmp_path, MagicMock(), _engine=engine)
    resp = TestClient(app).get("/api/download/testamente/1")
    assert "text/markdown" in resp.headers["content-type"]
    assert ".md" in resp.headers["content-disposition"]


def test_download_txt_format(tmp_path: Path):
    engine = _make_engine()
    engine.get_history.return_value = [{"role": "user", "content": "test"}]
    app = _create_app(tmp_path, MagicMock(), _engine=engine)
    resp = TestClient(app).get("/api/download/testamente/1?fmt=txt")
    assert "text/plain" in resp.headers["content-type"]
    assert ".txt" in resp.headers["content-disposition"]


# ── GET / ──────────────────────────────────────────────────────

def test_index_html_served(client: TestClient):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "JuraKlar" in resp.text
    assert "jk-root" in resp.text
    assert "/api/advisors" in resp.text
