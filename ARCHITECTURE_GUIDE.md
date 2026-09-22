# ClearPath Justice Agent - Architecture Guide

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
Rules Engine (app/rules/eligibility.py)

Input: User screening answers
│
├─ Validate input structure
├─ Check required fields
└─ Format for assessment
│
↓
PLACEHOLDER v0.1
│
├─ Do NOT invent criteria
├─ Do NOT assume eligibility
├─ Route to human review
└─ Request verified rules
│
↓
FUTURE v0.2
│
├─ Check conviction eligibility
│  └─ Cannabis for Private Purposes Act Section X
├─ Check temporal eligibility
│  └─ CPPA effective date rules
├─ Check sentence completion
│  └─ Verified from user/government sources
├─ Check for disqualifying factors
│  └─ Current DOJ policy
└─ Identify required documents
   └─ Official checklist
│
↓
Output: EligibilityAssessment
│
├─ status: "eligible" | "not_eligible" | 
│           "needs_more_info" | "requires_human_review" | "unknown"
├─ reasons: [list of assessment reasons]
├─ next_steps: [list of recommended actions]
├─ documents_required: [list of documents]
└─ requires_human_review: boolean
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
├─ source: Original authoritative source
├─ source_type: "official" | "verified" | "curated"
├─ date_verified: When last verified
├─ jurisdiction: "South Africa"
└─ version: Version number

PRINCIPLE: No invented information
           Only verified materials
           Always cite source
           Never outdated
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
│  │  └─ GET /health returns 200
│  ├─ test_eligibility.py
│  │  └─ Rules engine returns structured output
│  └─ test_agent.py
│     └─ Agent processes messages correctly
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

## Future Expansions (v0.2+)

```
Current v0.1
│
├─ Rules: Placeholder
├─ Knowledge: Structure only
└─ Features: Core agent working
│
↓
v0.2: Verified Content
│
├─ Rules: Implement CPPA rules
├─ Knowledge: Add materials
├─ Features: Five-question screening, document generation
└─ Database: Add PostgreSQL
│
↓
v0.3: Advanced Features
│
├─ WhatsApp Integration: Paige connection
├─ Multi-language: Localization support
├─ Tracking: Application status
└─ Notifications: SMS/Email updates
│
↓
v0.4+: Expansion
│
├─ Broader Legal: Beyond cannabis
├─ Government Integration: DPI systems
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
