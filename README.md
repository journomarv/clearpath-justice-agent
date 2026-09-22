# ClearPath Justice Agent

**AI-assisted navigation for cannabis criminal-record expungement in South Africa**

## Core Principle

> **"AI assists; it does not adjudicate."**

ClearPath Justice Agent helps people navigate the cannabis conviction expungement process under South Africa's **Cannabis for Private Purposes Act 7 of 2024**. The agent provides information, guidance, and document preparation — but never makes final legal determinations. Legal eligibility assessments come from verified rules, human expertise, and authoritative sources, not from the AI.

## What This Is

A **real MVP foundation** for a digital justice platform that automates access to criminal-record relief. Not a chatbot demo — a production-ready system designed for:

- WhatsApp integration (via Paige)
- Web and mobile interfaces
- Expansion to broader legal-remedy navigation
- Integration with Department of Justice systems

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
ClearPath Justice Agent API
        ↓
Agent Orchestrator
   ↙          ↘
Rules Engine   Knowledge Base
   ↓             ↓
   └──────┬──────┘
          ↓
      DeepSeek
          ↓
   Agent Response
```

### The Hierarchy

1. **Verified ClearPath rules** (authoritative)
2. **Approved knowledge** (official documents, forms, procedures)
3. **Agent orchestration** (connects rules + knowledge)
4. **DeepSeek language generation** (explains and contextualizes)

The LLM does **NOT** determine legal eligibility. That's the job of the rules engine.

## Technology Stack

- **Backend**: Python 3.10+
- **Framework**: FastAPI
- **Data validation**: Pydantic
- **LLM Integration**: DeepSeek API
- **Testing**: pytest
- **CI/CD**: GitHub Actions
- **Architecture**: Cloud-ready, no local GPU required

## Project Status: v0.1 (Current)

This is the **working MVP foundation**. All core components are in place:

- ✅ FastAPI application
- ✅ DeepSeek integration
- ✅ Rules engine (placeholder architecture)
- ✅ Knowledge base (placeholder structure)
- ✅ Document tools
- ✅ Referral system
- ✅ Health checks
- ✅ Security-first design
- ✅ Tests and CI/CD
- ✅ Zero secrets in codebase

**Not implemented in v0.1:**
- Actual eligibility rules (pending ClearPath legal verification)
- Knowledge base content (pending ClearPath materials)
- Five-question screening logic (structure exists, awaiting implementation)
- Database persistence (coming in v0.2)
- WhatsApp integration (API ready, awaiting Paige connection)

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/journomarv/clearpath-justice-agent
cd clearpath-justice-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
nano .env
```

You **must** provide:
```
DEEPSEEK_API_KEY=your_api_key_here
```

Get your key from: https://platform.deepseek.com/api_keys

### Running the Server

```bash
# Start development server
python -m uvicorn app.main:app --reload

# Server runs on http://127.0.0.1:8000
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_health.py

# Run specific test
pytest tests/test_health.py::test_health_check
```

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "clearpath-justice-agent",
  "version": "0.1.0",
  "checks": {
    "api": true,
    "configuration": true,
    "deepseek_available": true
  }
}
```

### Chat

```bash
POST /chat
```

Request:
```json
{
  "message": "I want to know if I can expunge my cannabis conviction",
  "user_id": "optional-user-id",
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "message": "I can help you with that. Let me ask some clarifying questions...",
  "next_action": "ask_screening_questions",
  "requires_human": false,
  "confidence": 0.8,
  "sources": []
}
```

## Directory Structure

```
clearpath-justice-agent/
├── README.md                 # This file
├── .gitignore               # Never commit secrets
├── .env.example             # Configuration template
├── requirements.txt         # Python dependencies
├── pytest.ini              # Testing configuration
│
├── app/                     # Main application
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── agent.py             # Agent orchestrator
│   ├── deepseek.py          # DeepSeek API client
│   │
│   ├── rules/               # Eligibility rules engine
│   │   ├── __init__.py
│   │   └── eligibility.py   # Eligibility assessment
│   │
│   ├── knowledge/           # Verified information
│   │   ├── __init__.py
│   │   └── README.md        # Knowledge base structure
│   │
│   ├── tools/               # Agent tools
│   │   ├── __init__.py
│   │   ├── eligibility.py   # Eligibility checking
│   │   ├── documents.py     # Document management
│   │   └── referrals.py     # Referral handling
│   │
│   └── schemas/             # Pydantic data schemas
│       ├── __init__.py
│       └── agent.py         # API schemas
│
├── tests/                   # Test suite
│   ├── test_health.py       # Health check tests
│   ├── test_eligibility.py  # Rules engine tests
│   └── test_agent.py        # Agent tests
│
└── .github/
    └── workflows/
        └── tests.yml        # CI/CD configuration
```

## Security

This application may eventually handle sensitive justice-related information. Security is built in from the start:

### Secrets Management

- ✅ API keys passed via environment variables only
- ✅ `.env` is in `.gitignore` — never committed
- ✅ `.env.example` shows required configuration
- ✅ No secrets in logs, responses, or error messages
- ✅ DeepSeek key never exposed to frontend

### Data Handling

- ✅ Data minimization by design
- ✅ No unnecessary personal information collection
- ✅ Sensitive fields clearly marked
- ✅ Audit trail support (v0.2)
- ✅ Role-based access (future)

### Code Quality

- ✅ Type hints throughout
- ✅ Pydantic validation on all inputs
- ✅ Error handling that never exposes secrets
- ✅ Security tests in CI/CD
- ✅ Bandit and Safety checks

## Development

### Adding Verified Rules (v0.2)

When implementing eligibility rules:

1. Get authoritative source (CPPA, DOJ guidance, ClearPath legal team)
2. Add source comment with legislation section
3. Mark with verification date and reviewer
4. Test against known cases
5. Never invent or assume criteria

Example:

```python
# Source: Cannabis for Private Purposes Act 7 of 2024, Section 10
# Verified by: [ClearPath Legal Reviewer Name]
# Date: 2024-09-22

def check_conviction_eligibility(conviction_type: str) -> bool:
    """Check if conviction is eligible for expungement"""
    eligible_types = [
        "cannabis_possession",
        # ... verified cannabis-related offences
    ]
    return conviction_type in eligible_types
```

### Adding Knowledge Content (v0.2)

When adding to the knowledge base:

1. Verify source (DOJ, SAPS, ClearPath)
2. Add metadata with source and date
3. Include version information
4. Never fabricate information

### Future Enhancements

#### v0.2: Verified Rules & Knowledge

- [ ] Implement verified eligibility rules from ClearPath
- [ ] Add official expungement process guide
- [ ] Populate document checklist
- [ ] Add SAPS police clearance procedures
- [ ] Database persistence (PostgreSQL)
- [ ] Session management
- [ ] Assessment caching

#### v0.3: Advanced Features

- [ ] WhatsApp/Paige integration
- [ ] Multi-language support
- [ ] Application tracking
- [ ] Status notifications
- [ ] Audit logging
- [ ] User consent management

#### v0.4+: Expansion

- [ ] Broader legal-remedy navigation (not just cannabis)
- [ ] Government system integration
- [ ] Mobile application
- [ ] Advanced analytics
- [ ] Self-hosted model support
- [ ] Open-source model options

## Getting Help

### For ClearPath Team Members

- Legal questions: Contact ClearPath legal team
- Architecture questions: See code comments and this README
- Issues: Open GitHub issue with [v0.1] tag

### For Users

- Help with the application: Visit ClearPath Justice website
- Legal assistance: Contact referral organizations

## Production Deployment

The application is designed for cloud deployment:

```bash
# Using Docker (example)
docker build -t clearpath-justice-agent .
docker run -e DEEPSEEK_API_KEY=$KEY -p 8000:8000 clearpath-justice-agent

# Using AWS/GCP/Azure
# Follow standard containerized application deployment
```

**Important for production:**

- [ ] Set `ENVIRONMENT=production`
- [ ] Use managed secrets (AWS Secrets Manager, etc.)
- [ ] Enable HTTPS/TLS
- [ ] Set up monitoring and logging
- [ ] Configure appropriate CORS
- [ ] Enable rate limiting
- [ ] Set up database (PostgreSQL)
- [ ] Enable audit logging
- [ ] Review security checklist

## License

ClearPath Justice Agent is developed as part of the ClearPath Justice initiative.
For licensing details, see LICENSE file.

## Contributing

ClearPath Justice welcomes contributions that:

- Improve code quality and testing
- Enhance security
- Add documentation
- Fix bugs
- Optimize performance

**Do NOT contribute:**

- Invented legal rules
- Unverified information
- API keys or secrets
- Code that violates guidelines

## Acknowledgments

**ClearPath Justice Agent** is built to serve people navigating criminal-record relief in South Africa, guided by the principle that justice system access should be clear, fair, and accessible to all.

---

**Version**: 0.1.0  
**Last Updated**: 2024-09-22  
**Status**: Production-ready MVP foundation  
**Next**: v0.2 with verified rules and knowledge base

For questions or contributions, contact the ClearPath Justice team.
