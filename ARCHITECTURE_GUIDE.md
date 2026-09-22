# ClearPath Justice Agent - Architecture Guide

## v0.2 Summary

v0.2 generalises v0.1's cannabis-only skeleton into a **modular
relief-type architecture**, without inventing any legal content:

- `app/rules/registry.py` adds a plug-in pattern (`@register(ReliefType.X)`)
  so relief types are registered independently of the orchestrator.
- `app/rules/cannabis_cppa.py` (v0.1's original scope) and
  `app/rules/criminal_record_expungement.py` (new, general Criminal
  Procedure Act relief) both exist as **placeholder handlers**: every
  assessment still routes to `REQUIRES_HUMAN_REVIEW` with
  `verified_rules_applied=False`, because no relief type has been signed
  off by ClearPath legal yet.
- `app/knowledge/sources.py` adds a source-of-truth registry with a
  `content_verified_for_automation` flag, separating "safe to cite to a
  user" from "safe to encode as pass/fail logic".
- `app/privacy.py` adds ID-number/phone-number detection, wired into
  request validation and logging.
- `GET /relief-types` lets client surfaces discover supported relief
  types dynamically.

The rest of this document describes the full system; sections below are
updated in place to reflect the v0.2 structure.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACES                             │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│   WhatsApp   │     Web      │   Mobile     │  Advice Offices   │
│   (Paige)    │  (Browser)   │    App       │   (Future)        │
└──────┬───────┴──────┬───────┴──────┬───────┴─────────┬──────────┘
       │              │              │                 │
       └──────────────┼──────────────┼─────────────────┘
                      ↓
    ┌──────────────────────────────────────────────────────┐
    │     ClearPath Justice Agent API (FastAPI)            │
    ├──────────────────────────────────────────────────────┤
    │  POST /chat                                          │
    │  GET  /health                                        │
    │  (Future: /assessment, /documents, /referral, etc.)  │
    └──────────┬───────────────────────────────────────────┘
               ↓
    ┌──────────────────────────────────────────────────────┐
    │         Agent Orchestrator (app/agent.py)            │
    ├──────────────────────────────────────────────────────┤
    │  1. Analyze user intent                              │
    │  2. Gather context (rules + knowledge)               │
    │  3. Check eligibility (if needed)                    │
    │  4. Build LLM context                                │
    │  5. Call DeepSeek for response                       │
    │  6. Determine next action                            │
    └──────────┬───────────────────────────────────────────┘
               ↓
       ┌───────┴───────┐
       ↓               ↓
  ┌─────────────┐  ┌─────────────────────────────────┐
  │Rules Engine │  │    Knowledge Base               │
  ├─────────────┤  ├─────────────────────────────────┤
  │Eligibility  │  │- Process guides                 │
  │Assessment   │  │- Document checklists            │
  │(CPPA rules) │  │- Official forms                 │
  │             │  │- SAPS procedures                │
  │             │  │- DOJ guidance                   │
  │             │  │- Referral organizations        │
  └──────┬──────┘  └────────────┬────────────────────┘
         │                      │
         └──────────┬───────────┘
                    ↓
      ┌─────────────────────────────┐
      │   Verified Information      │
      │                             │
      │- Cannabis for Private       │
      │  Purposes Act 7 of 2024      │
      │- Department of Justice      │
      │  procedures                 │
      │- Official requirements      │
      │- Current policies           │
      └────────┬────────────────────┘
               ↓
      ┌─────────────────────────────┐
      │    DeepSeek LLM API         │
      ├─────────────────────────────┤
      │- Natural language response  │
      │- Contextual explanation     │
      │- Process guidance           │
      │- Document instructions      │
      └────────┬────────────────────┘
               ↓
      ┌─────────────────────────────┐
      │    Structured Response      │
      ├─────────────────────────────┤
      │{                            │
      │  message: string            │
      │  next_action: string        │
      │  requires_human: boolean    │
      │  sources: array             │
      │}                            │
      └─────────────────────────────┘
```

## Key Principle: The Hierarchy

```
AUTHORITY HIERARCHY (Never Inverted)

1. Verified Rules (authoritative)
   ↓
   Cannabis for Private Purposes Act 7 of 2024
   Department of Justice official guidance
   ClearPath legal verification

2. Approved Knowledge (authoritative facts)
   ↓
   Official forms and procedures
   Government contact information
   Verified checklists
   Current requirements

3. Agent Orchestration (implementation)
   ↓
   Connects rules + knowledge
   Handles conversation flow
   Determines next steps

4. LLM Language Generation (explanation)
   ↓
   Explains results in plain language
   Provides context and guidance
   Never overrides rules

                    ⬜ NEVER INVERT ⬜
         LLM should NOT determine legal eligibility
         LLM should NOT invent requirements
         LLM should NOT fabricate procedures
```

## Data Flow: User Question → Agent Response

### Example Flow: Eligibility Check

```
USER INPUT
│
├─ Message: "Can I expunge my cannabis conviction?"
├─ User ID: optional
└─ Session ID: optional
│
↓
INTENT ANALYSIS
│
├─ Detect "eligibility" intent
└─ Recognize this requires rules engine
│
↓
CONTEXT GATHERING
│
├─ Load eligibility screening questions
├─ Check knowledge base for process info
└─ Prepare rules engine for assessment
│
↓
ELIGIBILITY ASSESSMENT
│
├─ Call: check_eligibility()
├─ Returns: {
│    status: "requires_human_review",
│    reasons: [...],
│    documents_required: [...],
│    next_steps: [...]
│  }
└─ Check if referral needed
│
↓
LLM CONTEXT BUILD
│
├─ System Prompt: "AI assists; it does not adjudicate"
├─ Assessment results (from rules engine)
├─ Knowledge context (from knowledge base)
├─ Conversation history (if any)
└─ Message: "Based on this information, explain..."
│
↓
DEEPSEEK LLM CALL
│
├─ Input: Structured message context
└─ Output: Natural language response
│
↓
RESPONSE BUILDING
│
├─ Message: LLM response
├─ Next action: "ask_screening_questions" | "refer_to_human" | etc.
├─ Requires human: true/false
├─ Confidence: 0.0 - 1.0
└─ Sources: [list of information sources]
│
↓
RETURN TO USER
│
{
  "message": "I can help you explore your expungement options...",
  "next_action": "ask_screening_questions",
  "requires_human": false,
  "confidence": 0.8,
  "sources": []
}
```

## Tools Architecture

### Eligibility Tool

```python
# app/tools/eligibility.py

async def check_eligibility(screening_answers: Dict) -> Dict:
    """
    Called by: Agent when user asks about eligibility
    Calls: Rules engine (app/rules/eligibility.py)
    Returns: Structured eligibility assessment
    
    Flow:
    screening_answers → rules_engine → assessment_result → formatted_response
    """
    assessment = assess_expungement_eligibility(screening_answers)
    referral_reason = identify_referral_need(assessment)
    return {
        "status": assessment.status,
        "assessment": assessment.dict(),
        "referral_needed": referral_reason is not None,
    }
```

### Documents Tool

```python
# app/tools/documents.py

async def generate_document_checklist(assessment: EligibilityAssessment):
    """
    Called by: Agent when user asks about required documents
    Calls: Rules engine (for verified requirements)
    Returns: Personalized document checklist
    """
    requirements = get_document_requirements(assessment)
    return {
        "success": True,
        "checklist": format_checklist(requirements),
    }
```

### Referral Tool

```python
# app/tools/referrals.py

async def create_referral(reason: ReferralReason, description: str):
    """
    Called by: Agent when matter requires human/legal review
    Returns: Referral with appropriate contacts and next steps
    
    Reasons:
    - UNCERTAIN_ELIGIBILITY
    - DISPUTED_RECORD
    - COMPLEX_CIRCUMSTANCES
    - LEGAL_ADVICE_NEEDED
    - VULNERABLE_USER
    - TECHNICAL_FAILURE
    - OUTSIDE_KNOWLEDGE_BASE
    """
    contacts = get_referral_contacts(reason)
    return {
        "referral": create_referral_object(reason, description, contacts),
        "message": "Your case has been referred to our support team",
    }
```

## Configuration Management

```
Environment Variables (Secure)
│
├─ DEEPSEEK_API_KEY
│  └─ Passed at runtime only
│     Never in code
│     Never in logs
│     Never in responses
│
├─ DEEPSEEK_MODEL
│  └─ Model identifier (e.g., "deepseek-chat")
│
├─ HOST
│  └─ Server host (default: 127.0.0.1)
│
├─ PORT
│  └─ Server port (default: 8000)
│
├─ ENVIRONMENT
│  └─ development | staging | production
│
└─ LOG_LEVEL
   └─ DEBUG | INFO | WARNING | ERROR | CRITICAL

            ↓

    Loaded by: app/config.py

            ↓

Settings singleton instance

            ↓

Used throughout application
(Never re-read environment)
```

## Rules Engine Architecture

```
app/rules/eligibility.py  (generic entry point — the ONLY function
                            the rest of the app calls)

Input: ScreeningAnswers { relief_type, answers, free_text_context }
│
↓
app/rules/registry.py
│
├─ get_handler(relief_type) → looks up a registered handler function
├─ No handler found → UNKNOWN / requires_human_review=True (never guesses)
└─ Handler found → call it
│
↓
Relief-type handler (e.g. app/rules/cannabis_cppa.py,
                          app/rules/criminal_record_expungement.py)
│
├─ v0.1 / v0.2 STATUS: PLACEHOLDER for every relief type
│  ├─ Do NOT invent criteria
│  ├─ Do NOT assume eligibility
│  ├─ Route to human review (status=REQUIRES_HUMAN_REVIEW)
│  ├─ verified_rules_applied = False
│  └─ Cite knowledge sources (source_ids), even if those sources are
│     themselves still TODO for legal verification
│
↓
FUTURE (once ClearPath legal verifies a relief type)
│
├─ Check conviction eligibility
│  └─ e.g. Cannabis for Private Purposes Act Section X (cited, verified)
├─ Check temporal eligibility
│  └─ e.g. effective-date rules
├─ Check sentence completion
│  └─ Verified from user/government sources
├─ Check for disqualifying factors
│  └─ Current DOJ policy
├─ Identify required documents
│  └─ Official checklist
└─ Set verified_rules_applied = True
│
↓
Output: EligibilityAssessment
│
├─ relief_type: ReliefType (cannabis_expungement | criminal_record_expungement | unknown)
├─ status: "eligible" | "not_eligible" |
│           "needs_more_info" | "requires_human_review" | "unknown"
├─ reasons: [list of assessment reasons]
├─ next_steps: [list of recommended actions]
├─ documents_required: [list of documents]
├─ requires_human_review: boolean
├─ verified_rules_applied: boolean  (NEW — always False until legal sign-off)
└─ source_ids: [knowledge source IDs this assessment is traceable to]

Modularity: adding a new relief type never touches this file or the
orchestrator (app/agent.py) — only registry.py's decorator and a new
handler module. See README.md, "Adding a New Relief Type".
```

## Knowledge Base Architecture

```
Knowledge Base (app/knowledge/__init__.py)

Structure:
│
├─ expungement_process_guide
│  ├─ source: "Department of Justice"
│  ├─ verified_date: "YYYY-MM-DD"
│  └─ content: "Step-by-step process..."
│
├─ document_checklist
│  ├─ source: "ClearPath Justice"
│  ├─ verified_date: "YYYY-MM-DD"
│  └─ content: "Required documents..."
│
├─ application_forms
│  ├─ source: "Department of Justice"
│  ├─ form_id: "DOJ-CPPA-001"
│  └─ url: "https://..."
│
├─ police_clearance_info
│  ├─ source: "South African Police Service"
│  ├─ verified_date: "YYYY-MM-DD"
│  └─ content: "How to obtain certificate..."
│
├─ doj_procedures
│  ├─ source: "Department of Justice"
│  ├─ verified_date: "YYYY-MM-DD"
│  └─ content: "Institutional procedures..."
│
└─ referral_organizations
   ├─ source: "ClearPath Justice"
   ├─ organizations: [list of NGOs, legal aid, etc.]
   └─ verified_date: "YYYY-MM-DD"

Each item includes:
├─ source_ids: [IDs referencing app/knowledge/sources.py]
├─ relief_types: [which ReliefType(s) this applies to]
├─ content: plain-language text (TODO placeholder until populated)
└─ verified_date: When last verified (null until populated)

## Source Registry (NEW, v0.2)

```
app/knowledge/sources.py — SOURCE_REGISTRY

KnowledgeSource {
  id, title, organization,
  source_type: OFFICIAL | CURATED | UNVERIFIED,
  jurisdiction: "South Africa",
  url, verified_date,
  content_verified_for_automation: bool,  ← key distinction
  notes
}

content_verified_for_automation = False means:
  "Safe to CITE to a user as a pointer to an official process"
  ≠
  "Safe to ENCODE as pass/fail eligibility logic in app/rules/"

v0.2 ships several real OFFICIAL sources (e.g. justice.gov.za's
expungements overview, gov.za's summary page) found via public search —
all still content_verified_for_automation=False pending ClearPath legal
review of current wording and edge cases.
```

PRINCIPLE: No invented information
           Only verified materials
           Always cite source
           Never outdated
           Citing a source ≠ encoding it as automated logic
```

## API Request/Response Cycle

### Request

```json
POST /chat
Content-Type: application/json

{
  "message": "I want to know if I can expunge my cannabis conviction",
  "user_id": "optional-user-id",
  "session_id": "optional-session-id"
}
```

### Processing

```
1. FastAPI receives request
2. Pydantic validates structure (ChatRequest schema)
3. Agent.process_message() called
4. Intent analyzed
5. Context gathered
6. Tools called if needed
7. LLM response generated
8. Response formatted
```

### Response

```json
{
  "message": "I can help you understand your expungement options...",
  "next_action": "ask_screening_questions",
  "requires_human": false,
  "confidence": 0.8,
  "sources": [
    {
      "title": "Cannabis for Private Purposes Act 7 of 2024",
      "source_type": "official",
      "verified_date": "2024-09-22"
    }
  ]
}
```

## Testing Architecture

```
pytest (test framework)
│
├─ Unit Tests (no external dependencies)
│  ├─ test_health.py
│  │  └─ GET /health returns 200, never exposes the API key
│  ├─ test_eligibility.py
│  │  └─ Every relief type routes to human review, never fabricates
│  │     an eligible/not_eligible outcome (verified_rules_applied=False)
│  ├─ test_rules_registry.py  (NEW)
│  │  └─ Registry contains expected relief types; unsupported types
│  │     degrade safely instead of crashing
│  ├─ test_knowledge.py  (NEW)
│  │  └─ Every knowledge item cites a real, registered source
│  ├─ test_privacy.py  (NEW)
│  │  └─ ID-number / phone-number detection, redaction, and request
│  │     validation reject likely identifiers
│  └─ test_agent.py
│     └─ Agent processes messages correctly; DeepSeek failures fail
│        safe to human referral rather than crashing
│
├─ Fixtures
│  └─ TestClient for FastAPI
│
├─ Mocking
│  └─ DeepSeek API mocked (no real calls during tests)
│
├─ Coverage
│  └─ Target: 80%+ coverage of core logic
│
└─ CI/CD (GitHub Actions)
   ├─ Run on push to main/develop
   ├─ Run on pull requests
   ├─ Test Python 3.10, 3.11, 3.12
   ├─ Lint with flake8
   ├─ Type check with mypy
   ├─ Security check with bandit
   └─ Dependency check with safety
```

## Security Architecture

```
Secret Management
│
├─ Environment Variables Only
│  ├─ DEEPSEEK_API_KEY
│  └─ Never in code/logs/responses
│
├─ .env File (Local Only)
│  ├─ Gitignored
│  └─ Never committed
│
├─ .env.example (Template)
│  ├─ Shows required variables
│  └─ Uses placeholder values
│
└─ Configuration Validation
   ├─ Fails if API key missing
   └─ Fails if API key invalid

Input Validation
│
├─ Pydantic schemas
├─ Type checking
├─ Length limits
├─ Format validation
└─ SQL injection prevention (ready for DB)

Error Handling
│
├─ Never expose secrets
├─ User-friendly messages
├─ Detailed logging (internal only)
├─ Stack traces (hidden in production)
└─ Audit trail (ready for v0.2)

Data Protection
│
├─ HTTPS enforced (production)
├─ CORS configured
├─ Rate limiting (ready for v0.2)
├─ Input sanitization
└─ Sensitive field marking
```

## Deployment Architecture

### Development

```bash
python -m uvicorn app.main:app --reload
# http://127.0.0.1:8000
```

### Production (Docker Example)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

```
Container → Cloud Run / ECS / App Service
          ↓
Environmental Configuration (secrets)
          ↓
Load Balancer → Multiple Instances
          ↓
Database (PostgreSQL) → Session/User Data
          ↓
Logging Service → Audit Trail
          ↓
Monitoring → Health Checks
```

## Future Expansions

```
v0.1 (done)
│
├─ Rules: Placeholder (cannabis-only shape)
├─ Knowledge: Structure only
└─ Features: Core agent working
│
↓
v0.2 (this version)
│
├─ Rules: Modular registry; cannabis + general criminal-record relief
│         types both scaffolded, both still placeholder pending legal sign-off
├─ Knowledge: Source-of-truth registry with real reference URLs, content
│             still placeholder pending ClearPath material
├─ Privacy: PII detection/redaction wired into requests and logging
├─ API: GET /relief-types for dynamic client menus
└─ Tests: Registry, knowledge, and privacy coverage added
│
↓
v0.3: Verified Content + Advanced Features
│
├─ Rules: Implement verified criteria for at least one relief type
├─ Knowledge: Populate real process guides, checklists, referral contacts
├─ WhatsApp Integration: Paige connection
├─ Multi-language: Localization support
├─ Database: Add PostgreSQL, session management
└─ Tracking: Application status, notifications
│
↓
v0.4+: Expansion
│
├─ Additional relief types (e.g. Child Justice Act records)
├─ Government Integration: DOJ/SAPS systems
├─ Mobile App: Native iOS/Android
└─ Open Source: Self-hosted options
```

## Monitoring & Observability (v0.2)

```
Logging
├─ Application logs (FastAPI)
├─ LLM call logs (requests/responses, no PII)
└─ Error tracking

Metrics
├─ Request count
├─ Response time
├─ Error rate
└─ Assessment distribution

Tracing
├─ Request ID tracking
├─ Service dependencies
└─ Performance analysis

Audit Trail
├─ User actions
├─ Eligibility assessments
├─ Referrals created
└─ Data access
```

---

**This architecture is designed to be:**
- Secure (secrets never exposed)
- Transparent (clear separation of concerns)
- Scalable (cloud-ready)
- Maintainable (well-documented)
- Verifiable (comprehensive tests)
- Extensible (ready for v0.2+)

**Core Principle**: AI assists; it does not adjudicate.
