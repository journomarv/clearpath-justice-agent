# ClearPath Justice Agent

**AI-assisted navigation for criminal-record relief in South Africa**

## Core Principle

> **"AI assists; it does not adjudicate."**

ClearPath Justice Agent helps people navigate criminal-record relief and expungement processes in South Africa. The agent provides information, guidance, and document preparation — but never makes final legal determinations. Legal eligibility assessments come from verified rules, human expertise, and authoritative sources, not from the LLM.

## What This Is

A **modular MVP foundation** for a digital justice platform that automates access to criminal-record relief — designed from the ground up to cover more than one type of relief, not just cannabis expungement. Built for:

- WhatsApp integration (via Paige)
- Web and mobile interfaces
- Expansion across relief types as ClearPath verifies more legal criteria
- Integration with Department of Justice / SAPS systems

## Project Journey: Assess → Prepare → Manage → Refer → Verify

1. **Assess**: Ask required questions to understand the user's situation
2. **Prepare**: Generate personalized checklists and guidance
3. **Manage**: Track application progress and status
4. **Refer**: Connect users with appropriate legal/government support
5. **Verify**: Ensure applications meet all requirements before submission

## Architecture

```
WhatsApp / Paige / Web
        ↓
ClearPath Justice Agent API (FastAPI)
        ↓
Agent Orchestrator
   ↙          ↘
Rules Engine   Knowledge Base
(modular,        (DOJ / SAPS /
 per relief       ClearPath
 type)            sources)
   ↓             ↓
   └──────┬──────┘
          ↓
      DeepSeek
          ↓
   Agent Response
```

### The Hierarchy

1. **Verified ClearPath rules** (authoritative) — `app/rules/`
2. **Approved knowledge** (official documents, forms, procedures) — `app/knowledge/`
3. **Agent orchestration** (connects rules + knowledge) — `app/agent.py`
4. **DeepSeek language generation** (explains and contextualizes)

The LLM does **NOT** determine legal eligibility. That's the job of the rules engine — see `app/rules/eligibility.py` and `app/rules/registry.py`.

## What's New in v0.2

v0.1 built the skeleton for a **cannabis-only** flow with placeholder rules.
v0.2 generalises that skeleton into a **modular relief-type architecture**
and adds the machinery needed before real legal content can be plugged in:

- **`app/rules/registry.py`** — a plug-in registry so any relief type
  (cannabis expungement, general Criminal Procedure Act expungement, and
  future types) can register a handler without touching the orchestrator.
- **`app/rules/cannabis_cppa.py`** and **`app/rules/criminal_record_expungement.py`**
  — two relief-type modules. **Both are still placeholders**: they always
  route to human review (`verified_rules_applied=False`) because ClearPath
  has not yet supplied legally verified criteria. Each file documents
  exactly what a legal reviewer needs to confirm before real logic can be
  added — see the `TODO(legal-verification, ...)` blocks in those files.
- **`app/knowledge/sources.py`** — a source-of-truth registry with real,
  currently-public DOJ/gov.za reference URLs for the general expungement
  process, each flagged `content_verified_for_automation=False` until
  ClearPath legal signs off on using their specific facts as automated
  logic (see that file's docstring for why citing ≠ encoding).
- **`app/privacy.py`** — PII guards (ID-number / phone-number detection
  and redaction) wired into request validation (`ChatRequest`,
  `ScreeningAnswers`) and into logging/referral text.
- **`GET /relief-types`** — a new endpoint so client surfaces (e.g. a
  WhatsApp menu) can discover which relief types are currently supported,
  without hard-coding a list.
- Expanded test suite (`tests/test_rules_registry.py`,
  `tests/test_knowledge.py`, `tests/test_privacy.py`) that specifically
  asserts **no relief type fabricates an eligible/not-eligible outcome**
  and every knowledge item cites a real source.

**Still not implemented (by design, pending ClearPath legal verification):**
- Actual eligibility criteria for any relief type
- Populated knowledge-base content (process guides, checklists, forms)
- Referral-organisation contact list
- Database persistence
- WhatsApp/Paige integration

## Technology Stack

- **Backend**: Python 3.10+
- **Framework**: FastAPI
- **Data validation**: Pydantic v2 / pydantic-settings
- **LLM Integration**: DeepSeek API
- **Testing**: pytest, pytest-asyncio
- **CI/CD**: GitHub Actions
- **Architecture**: Cloud-ready, no local GPU required

## Quick Start

### Installation

```bash
git clone https://github.com/journomarv/clearpath-justice-agent
cd clearpath-justice-agent

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
nano .env
```

You **must** provide:
```
DEEPSEEK_API_KEY=your_api_key_here
```

Get your key from: https://platform.deepseek.com/api_keys

### Running the Server

```bash
python -m uvicorn app.main:app --reload
# Server runs on http://127.0.0.1:8000
```

### Running Tests

```bash
pytest                          # all tests
pytest --cov=app                # with coverage
pytest tests/test_eligibility.py
```

## API Endpoints

### Health Check

```bash
GET /health
```

```json
{
  "status": "ok",
  "service": "clearpath-justice-agent",
  "version": "0.2.0",
  "checks": {
    "api": true,
    "configuration": true,
    "deepseek_available": true
  }
}
```

### Supported Relief Types (new in v0.2)

```bash
GET /relief-types
```

```json
{
  "relief_types": ["cannabis_expungement", "criminal_record_expungement"]
}
```

### Chat

```bash
POST /chat
```

Request:
```json
{
  "message": "Can I expunge my cannabis conviction?",
  "user_id": "optional-user-id",
  "session_id": "optional-session-id",
  "relief_type_hint": "cannabis_expungement"
}
```

Response:
```json
{
  "message": "I can help explain the process. Right now this type of case needs a human reviewer, since ClearPath hasn't yet finalized verified eligibility rules for it...",
  "next_action": "refer_to_human",
  "requires_human": true,
  "confidence": 0.5,
  "sources": [
    {
      "id": "doj_expungements_overview",
      "title": "Expungement of a Criminal Record (Criminal Procedure Act, 1977)",
      "source_type": "official",
      "verified_date": null,
      "url": "https://justice.gov.za/expungements.html"
    }
  ],
  "relief_type": "cannabis_expungement"
}
```

Note: `message` and `free_text_context` fields are validated to reject
apparent South African ID numbers or phone numbers — see `app/privacy.py`.

## Directory Structure

```
clearpath-justice-agent/
├── README.md
├── ARCHITECTURE_GUIDE.md
├── .gitignore
├── .env.example
├── requirements.txt
├── pytest.ini
│
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app + endpoints
│   ├── config.py                        # Environment-based configuration
│   ├── agent.py                         # Agent orchestrator
│   ├── deepseek.py                      # DeepSeek API client
│   ├── privacy.py                       # PII detection / redaction (NEW)
│   │
│   ├── rules/                           # Modular eligibility rules engine
│   │   ├── __init__.py                  # Registers all relief-type handlers
│   │   ├── registry.py                  # Plug-in registry (NEW)
│   │   ├── eligibility.py               # Generic orchestrator entry point
│   │   ├── cannabis_cppa.py             # CPPA relief type (placeholder)
│   │   └── criminal_record_expungement.py  # General CPA relief type (NEW, placeholder)
│   │
│   ├── knowledge/                       # Verified information
│   │   ├── __init__.py                  # KNOWLEDGE_STRUCTURE, retrieval helpers
│   │   ├── sources.py                   # Source-of-truth registry (NEW)
│   │   └── README.md                    # How to add verified content
│   │
│   ├── tools/                           # Agent tools
│   │   ├── __init__.py
│   │   ├── eligibility.py
│   │   ├── documents.py
│   │   └── referrals.py
│   │
│   └── schemas/                         # Pydantic data schemas
│       ├── __init__.py
│       ├── agent.py                     # API request/response schemas
│       └── rules.py                     # Relief type / assessment schemas (NEW)
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_agent.py
│   ├── test_eligibility.py
│   ├── test_rules_registry.py           # NEW
│   ├── test_knowledge.py                # NEW
│   └── test_privacy.py                  # NEW
│
└── .github/
    └── workflows/
        └── tests.yml
```

## Security & Privacy

### Secrets Management

- API keys passed via environment variables only
- `.env` is gitignored; `.env.example` shows required configuration
- No secrets in logs, responses, or error messages
- `Settings.__repr__` explicitly redacts the API key (see `app/config.py`)

### Data Minimization (v0.2)

- `app/privacy.py` detects likely South African ID numbers and phone
  numbers in free text and:
  - **Rejects** them at the API boundary (`ChatRequest.message`,
    `ScreeningAnswers.free_text_context`) — the agent asks users not to
    share identifiers in chat at all.
  - **Redacts** them before any text is logged or attached to a referral.
- Screening answers are designed to carry only what a rules handler
  actually needs (offence category, rough timing) — not names, ID
  numbers, or case numbers.

### Code Quality

- Type hints throughout
- Pydantic v2 validation on all inputs
- Security tests in CI/CD (bandit, safety)

## Development

### Adding a New Relief Type (v0.2 architecture)

1. Add a value to `ReliefType` in `app/schemas/rules.py`.
2. Create `app/rules/<new_relief_type>.py` with a function decorated
   `@register(ReliefType.YOUR_NEW_TYPE)`. Until legal criteria are
   verified, it must return `EligibilityStatus.REQUIRES_HUMAN_REVIEW` /
   `UNKNOWN` with `verified_rules_applied=False` — see
   `app/rules/cannabis_cppa.py` for the required documentation format.
3. Import the new module in `app/rules/__init__.py`.
4. Add matching entries to `app/knowledge/sources.py` and
   `app/knowledge/__init__.py`.
5. Add tests mirroring `tests/test_eligibility.py`.

### Adding Verified Rules (once ClearPath legal signs off)

```python
# Source: Cannabis for Private Purposes Act 7 of 2024, Section X
# Verified by: [ClearPath Legal Reviewer Name]
# Date: YYYY-MM-DD

def check_conviction_eligibility(conviction_type: str) -> bool:
    """Check if conviction is eligible for expungement."""
    eligible_types = [
        "cannabis_possession",
        # ... verified cannabis-related offences
    ]
    return conviction_type in eligible_types
```

Never add a threshold, date, fee, or disqualifying factor without a
section citation and reviewer sign-off (see the `TODO(legal-verification)`
blocks in `app/rules/`).

### Adding Knowledge Content

See `app/knowledge/README.md` for the full workflow: verify the source,
update `app/knowledge/sources.py`, then update the matching item's
`content` in `app/knowledge/__init__.py`.

### Future Enhancements

#### v0.3: Advanced Features
- [ ] WhatsApp/Paige integration
- [ ] Multi-language support
- [ ] Application tracking
- [ ] Status notifications
- [ ] Audit logging
- [ ] User consent management

#### v0.4+: Expansion
- [ ] Additional relief types (e.g. Child Justice Act records)
- [ ] Government system integration
- [ ] Mobile application
- [ ] Advanced analytics

## Production Deployment

```bash
docker build -t clearpath-justice-agent .
docker run -e DEEPSEEK_API_KEY=$KEY -p 8000:8000 clearpath-justice-agent
```

**Important for production:**

- [ ] Set `ENVIRONMENT=production`
- [ ] Use managed secrets (AWS Secrets Manager, etc.)
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring and logging
- [ ] Configure appropriate CORS (`CORS_ORIGINS`)
- [ ] Enable rate limiting
- [ ] Set up database (PostgreSQL)
- [ ] Enable audit logging
- [ ] Complete legal verification before enabling any relief type's rules

## License

ClearPath Justice Agent is developed as part of the ClearPath Justice initiative. For licensing details, see LICENSE file.

## Contributing

**Do NOT contribute:**
- Invented legal rules
- Unverified information
- API keys or secrets
- Code that violates guidelines

---

**Version**: 0.2.0
**Status**: Modular MVP foundation — rules engine architecture ready, legal content pending ClearPath verification
**Next**: v0.3 with database persistence and WhatsApp/Paige integration

For questions or contributions, contact the ClearPath Justice team.
