"""Multi-advisor RAG engine with per-(advisor, service) ChatEngine instances.

Each (advisor_id, service_id) combination gets its own ChatEngine instance
with its own BM25 index and conversation history. ChatEngine instances are
lazy-loaded on first use.

Note: AdvisorEngine is a single shared server instance. History is not
isolated per browser session — designed for single-user local use.
"""
from __future__ import annotations

import re
import types
from dataclasses import dataclass, field
from pathlib import Path

from ..llm.base import BaseLLMClient
from .chat_engine import ChatEngine


@dataclass
class ServiceConfig:
    """Configuration for a single advisory service."""
    id: int
    title: str
    category: str
    prompt: str  # System prompt body (frontmatter stripped)


@dataclass
class AdvisorConfig:
    """Configuration for a single legal advisor (e.g. testamente)."""
    id: str          # directory name, e.g. "testamente"
    title: str       # from index.md heading, e.g. "Testamente"
    services: list[ServiceConfig] = field(default_factory=list)
    wiki_dir: Path = field(default_factory=Path)


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Split YAML frontmatter from body using regex.

    Args:
        content: Full file content including optional frontmatter block.

    Returns:
        Tuple of (frontmatter_dict, body_text). If no frontmatter, returns
        empty dict and original content.
    """
    parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) == 3:
        fm: dict[str, str] = {}
        for line in parts[1].strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
        return fm, parts[2]
    return {}, content


def _make_chat_cfg(wiki_name: str, wiki_dir: Path, prompt_text: str) -> object:
    """Create a duck-typed config object compatible with ChatEngine.

    ChatEngine uses only three attributes of WikiConfig:
      - cfg.wiki_name  (str)
      - cfg.wiki_dir   (Path)
      - cfg.prompt_chat.read_text(encoding=...)  (str)

    Returns a SimpleNamespace that satisfies these without requiring a full
    WikiConfig (which would need many unused fields).
    """
    prompt_ns = types.SimpleNamespace(
        read_text=lambda encoding="utf-8": prompt_text
    )
    return types.SimpleNamespace(
        wiki_name=wiki_name,
        wiki_dir=wiki_dir,
        prompt_chat=prompt_ns,
    )


class AdvisorEngine:
    """Multi-advisor wrapper over ChatEngine.

    Discovers advisors from the filesystem, lazily creates and caches one
    ChatEngine per (advisor_id, service_id) combination.
    """

    def __init__(self, root: Path, llm: BaseLLMClient | None) -> None:
        self._root = root
        self._llm = llm
        self._advisors: dict[str, AdvisorConfig] | None = None
        self._engines: dict[tuple[str, int], ChatEngine] = {}

    def discover(self) -> dict[str, AdvisorConfig]:
        """Scan root/ and return all valid advisors.

        A directory is a valid advisor if it contains a prompts/ subdirectory
        with at least one .md file. Result is cached after the first call.
        """
        if self._advisors is not None:
            return self._advisors

        advisors: dict[str, AdvisorConfig] = {}
        for d in sorted(self._root.iterdir()):
            if not d.is_dir():
                continue
            prompts_dir = d / "prompts"
            if not prompts_dir.exists():
                continue
            prompt_files = sorted(prompts_dir.glob("*.md"), key=lambda p: p.name)
            if not prompt_files:
                continue

            # Parse advisor title from index.md first heading
            title = d.name.capitalize()
            index_file = d / "index.md"
            if index_file.exists():
                m = re.search(
                    r"^#\s+(.+)$",
                    index_file.read_text(encoding="utf-8"),
                    re.MULTILINE,
                )
                if m:
                    title = m.group(1).strip()

            # Parse services
            services: list[ServiceConfig] = []
            for f in prompt_files:
                fm, body = _parse_frontmatter(f.read_text(encoding="utf-8"))
                services.append(ServiceConfig(
                    id=int(fm.get("service_id", 0)),  # 0 if frontmatter missing — callers should ensure all prompt files have service_id
                    title=fm.get("title", f.stem),
                    category=fm.get("category", ""),
                    prompt=body.strip(),
                ))

            advisors[d.name] = AdvisorConfig(
                id=d.name,
                title=title,
                services=services,
                wiki_dir=d,
            )

        self._advisors = advisors
        return advisors

    def get_engine(self, advisor_id: str, service_id: int) -> ChatEngine:
        """Lazy-load and cache a ChatEngine for (advisor_id, service_id).

        On first call, builds the BM25 index from the advisor's wiki pages.
        """
        key = (advisor_id, service_id)
        if key not in self._engines:
            advisors = self.discover()
            if advisor_id not in advisors:
                raise KeyError(f"Unknown advisor '{advisor_id}'. Available: {list(advisors)}")
            advisor = advisors[advisor_id]
            service = next((s for s in advisor.services if s.id == service_id), None)
            if service is None:
                raise KeyError(f"Service {service_id} not found for advisor '{advisor_id}'")
            cfg = _make_chat_cfg(advisor.title, advisor.wiki_dir, service.prompt)
            engine = ChatEngine(cfg)  # type: ignore[arg-type]
            engine.build_index()
            self._engines[key] = engine
        return self._engines[key]

    async def ask(self, advisor_id: str, service_id: int, question: str) -> str:
        """Answer a question using the appropriate ChatEngine."""
        if self._llm is None:
            raise RuntimeError("AdvisorEngine was created without an LLM client. Pass llm= to __init__.")
        engine = self.get_engine(advisor_id, service_id)
        return await engine.ask(question, self._llm)

    def get_history(self, advisor_id: str, service_id: int) -> list[dict]:
        """Return conversation history for (advisor_id, service_id)."""
        key = (advisor_id, service_id)
        if key not in self._engines:
            return []
        return list(self._engines[key]._history)

    def clear(self, advisor_id: str, service_id: int) -> None:
        """Clear conversation history for (advisor_id, service_id).

        No-op if the combination has never been used.
        """
        key = (advisor_id, service_id)
        if key in self._engines:
            self._engines[key].clear_history()
