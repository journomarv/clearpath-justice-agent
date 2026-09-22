#!/usr/bin/env bash
set -euo pipefail

# --- Safety: refuse to run if DEEPSEEK_API_KEY is in tracked files -----------
if git ls-files -z 2>/dev/null | xargs -0 grep -l "DEEPSEEK_API_KEY=" 2>/dev/null | grep -v ".env.example" ; then
  echo "ERROR: DEEPSEEK_API_KEY assignment found in tracked files. Aborting."
  exit 1
fi

mkdir -p api app/routers app/services app/safety \
         knowledge/expungement knowledge/legal_framework knowledge/safeguards knowledge/rules \
         tests

# ---------------------------------------------------------------------------
# api/index.py
# ---------------------------------------------------------------------------
cat > api/index.py <<'PY'
"""Vercel serverless entrypoint for ClearPath Justice Agent."""
from app.main import app  # noqa: F401

__all__ = ["app"]
PY

# ---------------------------------------------------------------------------
# app/__init__.py
# ---------------------------------------------------------------------------
: > app/__init__.py
: > app/routers/__init__.py
: > app/services/__init__.py
: > app/safety/__init__.py
: > tests/__init__.py

# ---------------------------------------------------------------------------
# app/config.py
# ---------------------------------------------------------------------------
cat > app/config.py <<'PY'
"""Application settings. Secrets are read from environment only."""
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")
    deepseek_timeout_seconds: float = Field(default=30.0, alias="DEEPSEEK_TIMEOUT_SECONDS")
    deepseek_max_retries: int = Field(default=2, alias="DEEPSEEK_MAX_RETRIES")

    service_name: str = "ClearPath Justice Agent"
    environment: str = Field(default="production", alias="ENVIRONMENT")
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")

    @property
    def deepseek_configured(self) -> bool:
        return bool(self.deepseek_api_key and self.deepseek_api_key.strip())

    @property
    def cors_origin_list(self) -> list[str]:
        raw = (self.cors_origins or "").strip()
        if not raw or raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
PY

# ---------------------------------------------------------------------------
# app/models.py
# ---------------------------------------------------------------------------
cat > app/models.py <<'PY'
"""Pydantic models for API contracts."""
from typing import Literal, Optional
from pydantic import BaseModel, Field

PathwayId = Literal[
    "cannabis_related_relief",
    "general_expungement",
    "other_criminal_record_relief",
    "unknown",
]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = "ClearPath Justice Agent"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    pathway_hint: Optional[PathwayId] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    pathway: PathwayId = "unknown"
    knowledge_sources: list[str] = Field(default_factory=list)
    uncertainty: list[str] = Field(default_factory=list)
    next_step: str = ""


class AssessRequest(BaseModel):
    narrative: str = Field(..., min_length=1, max_length=6000)
    offence_category: Optional[str] = None
    has_completed_sentence: Optional[bool] = None
    years_since_conviction: Optional[int] = None


class AssessResponse(BaseModel):
    possible_pathway: PathwayId = "unknown"
    information_needed: list[str] = Field(default_factory=list)
    preliminary_guidance: str
    disclaimer: str
PY

# ---------------------------------------------------------------------------
# app/safety/guardrails.py
# ---------------------------------------------------------------------------
cat > app/safety/guardrails.py <<'PY'
"""Post-processing guardrails for AI output."""
from __future__ import annotations

import re

FORBIDDEN_PATTERNS = [
    (re.compile(r"\byou (are|will be) (definitely |certainly )?eligible\b", re.I),
     "AI cannot determine eligibility."),
    (re.compile(r"\byour (application|case) will (definitely |certainly )?succeed\b", re.I),
     "AI cannot guarantee outcomes."),
    (re.compile(r"\byour record (has been|is now) expunged\b", re.I),
     "Only the relevant authority can confirm expungement."),
    (re.compile(r"\bi am (a|your) lawyer\b", re.I),
     "ClearPath is not a lawyer."),
    (re.compile(r"\bcase (number|status)[:=]\s*\S+", re.I),
     "AI cannot issue or confirm case numbers."),
]

DISCLAIMER = (
    "ClearPath Justice Agent provides general information and process guidance "
    "only. It is not a lawyer, does not provide legal representation, and does "
    "not make official determinations. Only the relevant South African "
    "authority can confirm eligibility, status, or outcomes."
)


def scan(text: str) -> list[str]:
    flags: list[str] = []
    for pattern, note in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            flags.append(note)
    return flags
PY

# ---------------------------------------------------------------------------
# app/services/knowledge.py
# ---------------------------------------------------------------------------
cat > app/services/knowledge.py <<'PY'
"""Deterministic, lightweight knowledge retrieval."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

KNOWLEDGE_ROOT = Path(__file__).resolve().parents[2] / "knowledge"

PATHWAY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "cannabis_related_relief": (
        "cannabis", "dagga", "marijuana", "weed",
        "cannabis offence", "section 4", "drugs and drug trafficking",
    ),
    "general_expungement": (
        "expunge", "expungement", "criminal record", "clear record",
        "record relief", "criminal record expungement act",
    ),
    "other_criminal_record_relief": (
        "pardon", "presidential pardon", "amnesty", "record sealing",
        "section 271", "rehabilitation of offenders",
    ),
}

TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "eligibility": ("eligible", "eligibility", "qualify", "who can"),
    "process": ("process", "how do i", "steps", "procedure", "apply"),
    "required_documents": ("document", "documents", "papers", "fingerprint", "id"),
    "police_clearance": ("police clearance", "clearance certificate", "saps"),
    "submission": ("submit", "submission", "where do i send", "director-general"),
    "timelines": ("how long", "timeline", "duration", "weeks", "months"),
    "outcomes": ("outcome", "result", "what happens", "decision"),
    "exceptions": ("exception", "special case", "excluded", "not eligible"),
}

_PATHWAY_BY_STEM = {
    "cannabis_related_relief": "cannabis_related_relief",
    "general_expungement": "general_expungement",
    "criminal_record_relief": "other_criminal_record_relief",
    "expungement": "general_expungement",
}


@dataclass
class KnowledgeHit:
    source: str
    topic: str
    pathway: str
    content: str
    score: float = 0.0
    tags: list[str] = field(default_factory=list)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


@lru_cache(maxsize=1)
def _load_corpus() -> list[KnowledgeHit]:
    hits: list[KnowledgeHit] = []
    if not KNOWLEDGE_ROOT.exists():
        return hits
    for md in KNOWLEDGE_ROOT.rglob("*.md"):
        rel = md.relative_to(KNOWLEDGE_ROOT).as_posix()
        if rel == "README.md":
            continue
        category = rel.split("/")[0]
        topic = md.stem
        content = _read(md)
        if not content:
            continue
        pathway_id = _PATHWAY_BY_STEM.get(md.stem, "unknown")
        hits.append(KnowledgeHit(
            source=f"knowledge/{rel}", topic=topic, pathway=pathway_id,
            content=content, tags=[category, topic, pathway_id],
        ))
    return hits


@lru_cache(maxsize=1)
def _load_rules() -> list[dict]:
    rules_path = KNOWLEDGE_ROOT / "rules" / "expungement_rules.json"
    if not rules_path.exists():
        return []
    try:
        data = json.loads(rules_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data.get("rules", []) if isinstance(data, dict) else data


def detect_pathway(text: str, hint: str | None = None) -> str:
    if hint and hint != "unknown":
        return hint
    low = text.lower()
    scores = {p: sum(1 for kw in kws if kw in low) for p, kws in PATHWAY_KEYWORDS.items()}
    best = max(scores, key=scores.get) if scores else "unknown"
    return best if scores.get(best, 0) > 0 else "unknown"


def _detect_topics(text: str) -> list[str]:
    low = text.lower()
    found = [t for t, kws in TOPIC_KEYWORDS.items() if any(kw in low for kw in kws)]
    return found or ["process", "eligibility"]


def retrieve(query: str, pathway: str | None = None, top_k: int = 5) -> list[KnowledgeHit]:
    corpus = _load_corpus()
    if not corpus:
        return []
    low = query.lower()
    topics = set(_detect_topics(query))
    detected = detect_pathway(query, pathway)
    words = {w for w in re.findall(r"[a-z]{4,}", low)}
    scored: list[KnowledgeHit] = []
    for hit in corpus:
        score = 0.0
        if hit.topic in topics:
            score += 3.0
        if detected != "unknown" and detected == hit.pathway:
            score += 2.0
        content_words = set(re.findall(r"[a-z]{4,}", hit.content.lower()))
        score += min(len(words & content_words) * 0.1, 2.0)
        if score > 0:
            scored.append(KnowledgeHit(
                source=hit.source, topic=hit.topic, pathway=hit.pathway,
                content=hit.content, score=round(score, 3), tags=list(hit.tags),
            ))
    scored.sort(key=lambda h: h.score, reverse=True)
    return scored[:top_k]


def relevant_rules(query: str, pathway: str | None = None) -> list[dict]:
    rules = _load_rules()
    if not rules:
        return []
    detected = detect_pathway(query, pathway)
    low = query.lower()
    matches = []
    for rule in rules:
        topic = str(rule.get("topic", "")).lower()
        rule_text = str(rule.get("rule", "")).lower()
        if detected != "unknown" and detected in str(rule.get("pathways", [])).lower():
            matches.append(rule)
        elif any(word in low for word in topic.split() if len(word) > 3):
            matches.append(rule)
        elif any(word in low for word in rule_text.split() if len(word) > 6):
            matches.append(rule)
    return matches[:5]


def build_context(query: str, pathway_hint: str | None = None) -> dict:
    detected = detect_pathway(query, pathway_hint)
    hits = retrieve(query, detected)
    rules = relevant_rules(query, detected)

    context_parts: list[str] = []
    sources: list[str] = []
    for h in hits:
        context_parts.append(f"### SOURCE: {h.source}\n{h.content.strip()}")
        sources.append(h.source)
    for r in rules:
        context_parts.append(
            "### RULE: {id}\nTopic: {topic}\nRule: {rule}\nSource: {source}\n"
            "Effective: {effective_date}\nConfidence: {confidence}\nNotes: {notes}".format(
                id=r.get("id", "?"), topic=r.get("topic", ""), rule=r.get("rule", ""),
                source=r.get("source", ""), effective_date=r.get("effective_date", ""),
                confidence=r.get("confidence", ""), notes=r.get("notes", ""),
            )
        )
        sources.append(f"rules/{r.get('id', 'unknown')}")

    return {
        "pathway": detected,
        "context_text": "\n\n".join(context_parts),
        "sources": sources,
        "rules": rules,
    }
PY

# ---------------------------------------------------------------------------
# app/services/deepseek.py
# ---------------------------------------------------------------------------
cat > app/services/deepseek.py <<'PY'
"""Async DeepSeek client. Never logs or returns the API key."""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger("clearpath.deepseek")

SYSTEM_PROMPT = """You are ClearPath Justice Agent, a South African digital justice
assistant that helps people navigate criminal-record relief and expungement.

HARD RULES (never violate):
1. You assist; you do NOT adjudicate. Never declare someone eligible or ineligible.
2. Never guarantee an application will succeed.
3. Never invent legal rules, government procedures, fees, or timelines.
4. Never claim to be a lawyer or provide legal representation.
5. Never state that a record HAS been expunged.
6. Never fabricate case status, government communication, or reference numbers.
7. Only use the RETRIEVED KNOWLEDGE provided below. If it does not cover the
   question, say so explicitly and list what needs confirmation.
8. Clearly separate: (a) known information from sources, (b) information that
   requires confirmation, (c) missing information.
9. Do not assume the case is cannabis-related. Identify the applicable pathway.
10. Always end with the single most useful next step for the user.

RESPONSE FORMAT — always return valid JSON:
{
  "answer": "<plain-language answer>",
  "pathway": "<cannabis_related_relief | general_expungement |
                other_criminal_record_relief | unknown>",
  "uncertainty": ["<items you cannot confirm>", ...],
  "next_step": "<one concrete next action>"
}
"""


@dataclass
class DeepSeekResult:
    ok: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


class DeepSeekClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def configured(self) -> bool:
        return self.settings.deepseek_configured

    async def chat(self, user_message: str, retrieved_context: str, pathway: str) -> DeepSeekResult:
        if not self.configured:
            return DeepSeekResult(
                ok=False, error="DeepSeek API key is not configured.", status_code=None
            )

        url = f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        user_block = (
            f"USER QUESTION:\n{user_message}\n\n"
            f"DETECTED PATHWAY (may be 'unknown'): {pathway}\n\n"
            f"RETRIEVED KNOWLEDGE (authoritative for this answer):\n"
            f"{retrieved_context or '(no matching knowledge found)'}\n\n"
            "Respond with JSON only, per the required schema."
        )
        payload = {
            "model": self.settings.deepseek_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_block},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        attempts = max(1, self.settings.deepseek_max_retries + 1)
        last_error: str | None = None

        for attempt in range(attempts):
            try:
                async with httpx.AsyncClient(
                    timeout=self.settings.deepseek_timeout_seconds
                ) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    try:
                        body = resp.json()
                        content = body["choices"][0]["message"]["content"]
                        parsed = json.loads(content) if isinstance(content, str) else content
                        return DeepSeekResult(ok=True, data=parsed, status_code=200)
                    except (KeyError, IndexError, ValueError) as exc:
                        logger.warning("DeepSeek malformed response: %s", type(exc).__name__)
                        return DeepSeekResult(
                            ok=False,
                            error="Upstream returned an unexpected response shape.",
                            status_code=resp.status_code,
                        )
                if resp.status_code in (401, 403):
                    return DeepSeekResult(
                        ok=False,
                        error="DeepSeek authentication failed. Check the configured API key.",
                        status_code=resp.status_code,
                    )
                if resp.status_code == 429:
                    last_error = "DeepSeek rate limit reached."
                elif 500 <= resp.status_code < 600:
                    last_error = "DeepSeek upstream error."
                else:
                    last_error = f"DeepSeek request failed (status {resp.status_code})."
            except httpx.TimeoutException:
                last_error = "DeepSeek request timed out."
            except httpx.HTTPError as exc:
                last_error = f"Network error contacting DeepSeek ({type(exc).__name__})."

            if attempt < attempts - 1:
                await asyncio.sleep(0.5 * (attempt + 1))

        return DeepSeekResult(ok=False, error=last_error or "DeepSeek request failed.")
PY

# ---------------------------------------------------------------------------
# app/routers/health.py
# ---------------------------------------------------------------------------
cat > app/routers/health.py <<'PY'
from fastapi import APIRouter
from app.config import get_settings
from app.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service=get_settings().service_name)
PY

# ---------------------------------------------------------------------------
# app/routers/chat.py
# ---------------------------------------------------------------------------
cat > app/routers/chat.py <<'PY'
from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models import ChatRequest, ChatResponse
from app.safety.guardrails import DISCLAIMER, scan
from app.services.deepseek import DeepSeekClient
from app.services.knowledge import build_context

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    settings = get_settings()
    ctx = build_context(req.message, req.pathway_hint)

    client = DeepSeekClient(settings)
    if not client.configured:
        return ChatResponse(
            answer=(
                "The ClearPath assistant's language model is currently "
                "unavailable. You can still review the general information "
                "below, but please confirm specifics with the relevant "
                "South African authority."
            ),
            pathway=ctx["pathway"],
            knowledge_sources=ctx["sources"],
            uncertainty=["Language model not configured; answer is knowledge-only."],
            next_step="Retry later or contact the Department of Justice directly.",
        )

    result = await client.chat(req.message, ctx["context_text"], ctx["pathway"])
    if not result.ok or not result.data:
        raise HTTPException(
            status_code=502,
            detail={"error": "upstream_unavailable",
                    "message": result.error or "DeepSeek error"},
        )

    data = result.data
    answer = str(data.get("answer", "")).strip() or "No answer produced."
    uncertainty = list(data.get("uncertainty") or [])
    for flag in scan(answer):
        if flag not in uncertainty:
            uncertainty.append(flag)

    return ChatResponse(
        answer=f"{answer}\n\n{DISCLAIMER}",
        pathway=data.get("pathway", ctx["pathway"]) or "unknown",
        knowledge_sources=ctx["sources"],
        uncertainty=uncertainty,
        next_step=str(data.get("next_step", "")).strip(),
    )
PY

# ---------------------------------------------------------------------------
# app/routers/assess.py
# ---------------------------------------------------------------------------
cat > app/routers/assess.py <<'PY'
from fastapi import APIRouter

from app.models import AssessRequest, AssessResponse
from app.safety.guardrails import DISCLAIMER
from app.services.knowledge import build_context, detect_pathway, relevant_rules

router = APIRouter(tags=["assess"])


def _information_needed(req: AssessRequest, pathway: str) -> list[str]:
    needed: list[str] = []
    if req.offence_category is None:
        needed.append("The category of the offence (statutory reference if known).")
    if req.has_completed_sentence is None:
        needed.append("Whether the sentence (including any fine) has been fully completed.")
    if req.years_since_conviction is None:
        needed.append("Approximate number of years since conviction / completion.")
    if pathway == "unknown":
        needed.append("Whether the matter relates to a cannabis-related offence or another category.")
    needed.append("Whether the conviction is on the Criminal Record Centre (CRC) record.")
    return needed


@router.post("/assess", response_model=AssessResponse)
async def assess(req: AssessRequest) -> AssessResponse:
    pathway = detect_pathway(req.narrative, None)
    ctx = build_context(req.narrative, pathway)
    rules = relevant_rules(req.narrative, pathway)

    guidance_bits: list[str] = []
    if ctx["context_text"]:
        guidance_bits.append("Preliminary information drawn from ClearPath's curated knowledge base:")
        for hit in ctx["sources"][:5]:
            guidance_bits.append(f"- See {hit}")
    if rules:
        guidance_bits.append(
            "Relevant rules flagged for your situation (subject to confirmation): "
            + ", ".join(r.get("id", "?") for r in rules)
        )
    if not guidance_bits:
        guidance_bits.append(
            "Not enough information was matched in the knowledge base to offer "
            "preliminary guidance. Please provide more detail."
        )

    return AssessResponse(
        possible_pathway=pathway,
        information_needed=_information_needed(req, pathway),
        preliminary_guidance="\n".join(guidance_bits),
        disclaimer=DISCLAIMER,
    )
PY

# ---------------------------------------------------------------------------
# app/main.py
# ---------------------------------------------------------------------------
cat > app/main.py <<'PY'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import assess, chat, health

settings = get_settings()

app = FastAPI(
    title=settings.service_name,
    version="1.0.0",
    description="South African criminal-record relief & expungement navigator.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(assess.router)
PY

# ---------------------------------------------------------------------------
# vercel.json
# ---------------------------------------------------------------------------
cat > vercel.json <<'JSON'
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "functions": {
    "api/index.py": { "runtime": "python3.12", "maxDuration": 30 }
  },
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/index" }
  ]
}
JSON

# ---------------------------------------------------------------------------
# requirements.txt (runtime) + requirements-dev.txt
# ---------------------------------------------------------------------------
cat > requirements.txt <<'TXT'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
python-dotenv==1.0.0
TXT

cat > requirements-dev.txt <<'TXT'
-r requirements.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
flake8==6.1.0
mypy==1.7.1
bandit==1.7.5
safety==2.3.5
TXT

# ---------------------------------------------------------------------------
# .env.example / .gitignore
# ---------------------------------------------------------------------------
cat > .env.example <<'ENV'
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_TIMEOUT_SECONDS=30
CORS_ORIGINS=*
ENVIRONMENT=production
ENV

# Only add to .gitignore if these lines aren't already there
touch .gitignore
for line in ".env" ".env.*" "!.env.example" "__pycache__/" "*.py[cod]" ".venv/" "venv/" ".pytest_cache/" ".mypy_cache/" ".coverage" "htmlcov/" ".vercel/"; do
  grep -qxF "$line" .gitignore || echo "$line" >> .gitignore
done

# ---------------------------------------------------------------------------
# pyproject.toml
# ---------------------------------------------------------------------------
cat > pyproject.toml <<'TOML'
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
filterwarnings = ["ignore::DeprecationWarning"]

[tool.flake8]
max-line-length = 100
extend-ignore = ["E203", "W503"]

[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true
TOML

# ---------------------------------------------------------------------------
# knowledge/* — abbreviated content; extend later
# ---------------------------------------------------------------------------
cat > knowledge/README.md <<'MD'
# ClearPath Justice Knowledge Base

Curated, human-reviewed source material the assistant retrieves BEFORE
calling the LLM. The LLM must not answer from memory alone.

- `expungement/` — process guidance
- `legal_framework/` — statutory frameworks and pathway definitions
- `safeguards/` — AI principles, privacy, uncertainty
- `rules/` — structured JSON rules

Rules for authors:
1. Every claim traces to a named source.
2. Unverifiable requirements get `"confidence": "requires_verification"`.
3. Never invent fees, timelines, or procedures.
4. Mark superseded information under `exceptions.md`.

This knowledge base is **not** cannabis-only.
MD

cat > knowledge/legal_framework/general_expungement.md <<'MD'
# General Criminal-Record Expungement (South Africa)

> Status: TOPIC OVERVIEW — not legal advice.

South Africa provides statutory mechanisms to clear certain criminal records.
The primary instrument referenced by ClearPath is the Criminal Record
Expungement Act, 2024 (and predecessor provisions under the Criminal
Procedure Act, 1977, s 271).

ClearPath will NOT declare eligibility, guarantee outcomes, or confirm
expungement. Only the Department of Justice and Constitutional Development
(DoJ&CD) can do that.
MD

cat > knowledge/legal_framework/cannabis_related_relief.md <<'MD'
# Cannabis-Related Criminal-Record Relief

Cannabis-related relief is **one** pathway. Do not assume a matter is
cannabis-related.

Following the Constitutional Court's judgment in Minister of Justice v Prince
and subsequent legislative reform, cannabis-related criminal records became a
specific area of relief. The pathway identifier is `cannabis_related_relief`.
Presence of a cannabis-related conviction is not itself proof of eligibility.
MD

cat > knowledge/expungement/eligibility.md <<'MD'
# Eligibility — Overview

ClearPath does not determine eligibility. Factors commonly relevant:

- Category of offence (some categories are excluded).
- Whether the sentence has been fully completed.
- Time elapsed since completion.
- Whether the record is held by the Criminal Record Centre.
- Whether any prior expungement applications have been made.

Confirm eligibility with the Department of Justice and Constitutional Development.
MD

cat > knowledge/expungement/process.md <<'MD'
# Process — High Level

1. ASSESS — Understand the conviction and which pathway may apply.
2. PREPARE — Gather documents (see required_documents.md).
3. MANAGE — Submit and track the application.
4. REFER — Where ClearPath cannot help, refer to the authority.
5. VERIFY — The authority confirms the outcome (not ClearPath, not AI).

Exact steps, forms, and addresses must be confirmed with the DoJ&CD.
MD

cat > knowledge/expungement/required_documents.md <<'MD'
# Required Documents (typical)

> Confirm the current list with the DoJ&CD before submitting.

- Certified copy of ID.
- SAPS fingerprint form (SAPS 91(a) or equivalent).
- Police clearance certificate application.
- Court records / case number where available.
- Affidavit explaining the application.
- Proof of completion of sentence where applicable.

If a document is unavailable, note it as missing — do not fabricate it.
MD

cat > knowledge/expungement/police_clearance.md <<'MD'
# Police Clearance

A police clearance certificate is issued by SAPS Criminal Record Centre. It
reflects the record as held by SAPS at the time of issue. It is **not** proof
of expungement; the underlying record may still exist.
MD

cat > knowledge/expungement/submission.md <<'MD'
# Submission

Applications are generally directed to the Director-General: Department of
Justice and Constitutional Development. The exact submission channel must be
confirmed at the time of application. Never invent portal URLs or addresses.
MD

cat > knowledge/expungement/timelines.md <<'MD'
# Timelines

Processing times vary and are not guaranteed. ClearPath must not promise a
specific duration. Cite source-specific durations only if provided.
MD

cat > knowledge/expungement/outcomes.md <<'MD'
# Outcomes

Only the relevant authority can confirm the outcome. ClearPath and its AI
must never state that a record has been expunged.
MD

cat > knowledge/expungement/exceptions.md <<'MD'
# Exceptions & Superseded Guidance

- Pre-2024 guidance based on CPA s 271 is partially superseded by the
  Criminal Record Expungement Act, 2024. Do not present pre-2024 guidance as
  current law.
- Offence categories excluded from relief must not be speculated on beyond
  what the curated rules state.
MD

cat > knowledge/safeguards/ai_principles.md <<'MD'
# AI Principles

**AI assists, not adjudicates.**

- Provides information, not legal advice.
- Never declares eligibility or outcome.
- Never invents law or procedure.
- Cites retrieved knowledge; when absent, says so.
MD

cat > knowledge/safeguards/privacy.md <<'MD'
# Privacy

- Do not request unnecessary personal identifiers.
- Do not log user message content at INFO level.
- Do not persist user narratives without explicit consent.
- API keys and secrets are never echoed in responses, logs, or errors.
MD

cat > knowledge/safeguards/uncertainty.md <<'MD'
# Uncertainty Handling

Every answer separates:
1. Known — supported by retrieved knowledge.
2. Needs confirmation — plausible but unverified.
3. Missing — not available.

When uncertain, say so plainly.
MD

cat > knowledge/rules/expungement_rules.json <<'JSON'
{
  "version": "1.0.0",
  "description": "Structured expungement rules. Not legal advice.",
  "confidence_levels": [
    "statutory", "administrative", "clearpath_guidance",
    "requires_verification", "superseded"
  ],
  "rules": [
    {
      "id": "R-CAN-001",
      "topic": "cannabis pathway exists",
      "pathways": ["cannabis_related_relief"],
      "rule": "A distinct pathway exists for cannabis-related criminal-record relief, separate from general expungement.",
      "source": "knowledge/legal_framework/cannabis_related_relief.md",
      "effective_date": "2024-01-01",
      "confidence": "clearpath_guidance",
      "notes": "Cannabis pathway is one of several."
    },
    {
      "id": "R-GEN-001",
      "topic": "statutory basis",
      "pathways": ["general_expungement"],
      "rule": "General expungement is governed primarily by the Criminal Record Expungement Act, 2024, read with CPA s 271.",
      "source": "knowledge/legal_framework/general_expungement.md",
      "effective_date": "2024-01-01",
      "confidence": "requires_verification",
      "notes": "Confirm current consolidation with DoJ&CD."
    },
    {
      "id": "R-GEN-002",
      "topic": "eligibility determination",
      "pathways": ["general_expungement", "cannabis_related_relief", "other_criminal_record_relief"],
      "rule": "Only the relevant South African authority determines eligibility. ClearPath and its AI must never declare eligibility.",
      "source": "knowledge/safeguards/ai_principles.md",
      "effective_date": "2024-01-01",
      "confidence": "clearpath_guidance",
      "notes": "Hard safety rule."
    },
    {
      "id": "R-GEN-003",
      "topic": "sentence completion",
      "pathways": ["general_expungement"],
      "rule": "Completion of the sentence (including any fine) is commonly a precondition for relief.",
      "source": "knowledge/expungement/eligibility.md",
      "effective_date": "2024-01-01",
      "confidence": "requires_verification",
      "notes": "Verify precise statutory wording."
    },
    {
      "id": "R-GEN-004",
      "topic": "police clearance is not expungement",
      "pathways": ["general_expungement", "cannabis_related_relief"],
      "rule": "A police clearance certificate does not itself prove