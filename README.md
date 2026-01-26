# 🍯 Agentic Honey-Pot for Scam Detection & Intelligence Extraction

> HCL-GUVI Buildathon Jan-Feb 2026 | AI for Fraud Detection & User Safety

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered honeypot system that detects scam messages, autonomously engages scammers through believable conversations, and extracts actionable intelligence.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Development Plan](#-development-plan)
- [Setup Instructions](#-setup-instructions)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)

---

## Overview

This project implements an autonomous AI honeypot that:
- 🎯 Detects scam/fraudulent messages in real-time
- 🤖 Activates an AI agent to engage scammers
- 🎭 Maintains believable human-like personas
- 💬 Handles multi-turn conversations
- 🔍 Extracts intelligence (bank accounts, UPI IDs, phishing links)
- 📊 Reports results to evaluation endpoint

---

## 🛠️ Tech Stack

### Recommended Stack (Google ADK + Gemini)

| Layer | Technology | Why? |
|-------|------------|------|
| **Language** | Python 3.10+ | Rich AI/ML ecosystem, ADK native support |
| **Agent Framework** | Google ADK | Purpose-built for AI agents, multi-agent workflows |
| **LLM** | Gemini 2.5 Flash | Fast, 1M token context, free tier, function calling |
| **API Framework** | FastAPI | Async support, auto-docs, Pydantic validation |
| **Session Storage** | Redis / In-Memory | Fast session management for conversations |
| **Deployment** | Railway / Render / Cloud Run | Free tier, easy deployment |
| **Testing** | Pytest + ADK Evaluation | Built-in agent evaluation framework |

### Model Selection Guide

| Model | Best For | Speed | Intelligence | Free Tier |
|-------|----------|-------|--------------|-----------|
| `gemini-2.5-flash` | **Recommended** - Fast & reliable | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 60 RPM |
| `gemini-2.5-pro` | Complex reasoning | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Limited |
| `gemini-3-flash` | Latest features | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Preview |
| `gemini-2.5-flash-lite` | Maximum speed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ |

### Why Google ADK?

```
┌─────────────────────────────────────────────────────────────────┐
│              WHY GOOGLE ADK FOR HONEYPOT?                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🤖 Purpose-Built for Agents                                     │
│  ├── LlmAgent: Perfect for our honeypot persona                 │
│  ├── SequentialAgent: Detection → Engagement → Extraction       │
│  ├── LoopAgent: Multi-turn conversation handling                │
│  └── Built-in state management across turns                     │
│                                                                  │
│  🔧 Native Tool Support                                          │
│  ├── Function tools for intelligence extraction                 │
│  ├── Automatic function calling with Gemini                     │
│  └── Easy integration with external APIs (GUVI callback)        │
│                                                                  │
│  🧪 Built-in Evaluation Framework                                │
│  ├── Test agent responses systematically                        │
│  ├── Generate synthetic test cases                              │
│  └── Measure engagement quality                                 │
│                                                                  │
│  🚀 Production Ready                                             │
│  ├── Docker containerization support                            │
│  ├── Cloud Run / Vertex AI deployment                           │
│  └── Proper error handling & logging                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Alternative Stacks

| Component | Alternatives | Notes |
|-----------|--------------|-------|
| **Agent Framework** | LangChain, CrewAI, AutoGen | ADK is lighter, Gemini-optimized |
| **LLM** | OpenAI GPT-4, Claude, Groq | Gemini has best free tier |
| **Deployment** | AWS Lambda, Heroku, Vercel | Railway/Render are simpler |

---

## 📁 Project Structure

```
honey-pot/
├── 📄 README.md                 # This file
├── 📄 PROBLEM_STATEMENT.md      # Full problem details
├── 📄 SUMMARY.md                # Quick reference & submission guide
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example              # Environment variables template
├── 📄 .gitignore                # Git ignore rules
│
├── 📂 app/
│   ├── 📄 __init__.py
│   ├── 📄 main.py               # FastAPI application entry point
│   ├── 📄 config.py             # Configuration & environment variables
│   │
│   ├── 📂 api/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 routes.py         # API route definitions
│   │   ├── 📄 middleware.py     # Auth middleware (x-api-key)
│   │   └── 📄 dependencies.py   # Dependency injection
│   │
│   ├── 📂 models/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 request.py        # Pydantic request models
│   │   ├── 📄 response.py       # Pydantic response models
│   │   └── 📄 intelligence.py   # Intelligence extraction models
│   │
│   ├── 📂 agents/               # Google ADK Agents
│   │   ├── 📄 __init__.py
│   │   ├── 📄 honeypot_agent.py # Main honeypot LlmAgent
│   │   ├── 📄 detector_agent.py # Scam detection agent
│   │   ├── 📄 extractor_agent.py# Intelligence extraction agent
│   │   └── 📄 pipeline.py       # SequentialAgent workflow
│   │
│   ├── 📂 tools/                # ADK Function Tools
│   │   ├── 📄 __init__.py
│   │   ├── 📄 extraction.py     # Bank/UPI/URL extraction tools
│   │   ├── 📄 callback.py       # GUVI callback tool
│   │   └── 📄 patterns.py       # Regex patterns
│   │
│   ├── 📂 prompts/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 persona.py        # Human persona system prompts
│   │   ├── 📄 detection.py      # Scam detection prompts
│   │   └── 📄 extraction.py     # Intelligence extraction prompts
│   │
│   └── 📂 services/
│       ├── 📄 __init__.py
│       ├── 📄 session.py        # Session management
│       └── 📄 callback.py       # GUVI callback service
│
├── 📂 tests/
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py           # Pytest fixtures
│   ├── 📄 test_api.py           # API endpoint tests
│   ├── 📄 test_agents.py        # Agent behavior tests
│   └── 📄 test_extraction.py    # Intelligence extraction tests
│
└── 📂 scripts/
    ├── 📄 test_local.py         # Local testing script
    └── 📄 simulate_scammer.py   # Mock scammer for testing
```

---

## 📅 Development Plan

### Phase 1: Foundation (Day 1-2)
> **Goal:** Set up project structure and basic API

| Task | Priority | Est. Time | Status |
|------|----------|-----------|--------|
| Initialize project structure | 🔴 High | 1 hr | ⬜ |
| Set up FastAPI with basic routes | 🔴 High | 2 hr | ⬜ |
| Implement API key authentication | 🔴 High | 1 hr | ⬜ |
| Create Pydantic request/response models | 🔴 High | 2 hr | ⬜ |
| Set up environment configuration | 🔴 High | 1 hr | ⬜ |
| Basic health check endpoint | 🟡 Med | 30 min | ⬜ |

### Phase 2: Scam Detection (Day 3-4)
> **Goal:** Build reliable scam detection system

| Task | Priority | Est. Time | Status |
|------|----------|-----------|--------|
| Define scam detection criteria | 🔴 High | 2 hr | ⬜ |
| Implement keyword-based detection | 🔴 High | 2 hr | ⬜ |
| Add LLM-based intent analysis | 🔴 High | 3 hr | ⬜ |
| Create confidence scoring | 🟡 Med | 2 hr | ⬜ |
| Test with sample scam messages | 🔴 High | 2 hr | ⬜ |

### Phase 3: AI Agent (Day 5-7)
> **Goal:** Build conversational AI agent with human-like persona

| Task | Priority | Est. Time | Status |
|------|----------|-----------|--------|
| Design agent persona prompts | 🔴 High | 3 hr | ⬜ |
| Integrate Gemini/LLM API | 🔴 High | 2 hr | ⬜ |
| Implement session management | 🔴 High | 3 hr | ⬜ |
| Handle multi-turn conversations | 🔴 High | 4 hr | ⬜ |
| Add response adaptation logic | 🟡 Med | 3 hr | ⬜ |
| Implement self-correction | 🟡 Med | 2 hr | ⬜ |

### Phase 4: Intelligence Extraction (Day 8-9)
> **Goal:** Extract actionable intelligence from conversations

| Task | Priority | Est. Time | Status |
|------|----------|-----------|--------|
| Build regex patterns for extraction | 🔴 High | 3 hr | ⬜ |
| Extract bank account numbers | 🔴 High | 2 hr | ⬜ |
| Extract UPI IDs | 🔴 High | 2 hr | ⬜ |
| Extract phishing links | 🔴 High | 2 hr | ⬜ |
| Extract phone numbers | 🟡 Med | 1 hr | ⬜ |
| Identify suspicious keywords | 🟡 Med | 2 hr | ⬜ |
| LLM-based entity extraction | 🟡 Med | 3 hr | ⬜ |

### Phase 5: Integration & Callback (Day 10)
> **Goal:** Complete system integration and GUVI callback

| Task | Priority | Est. Time | Status |
|------|----------|-----------|--------|
| Integrate all components | 🔴 High | 3 hr | ⬜ |
| Implement GUVI callback service | 🔴 High | 2 hr | ⬜ |
| Add engagement metrics tracking | 🔴 High | 2 hr | ⬜ |
| End-to-end testing | 🔴 High | 3 hr | ⬜ |

### Phase 6: Deployment & Testing (Day 11-12)
> **Goal:** Deploy and validate with GUVI endpoint tester

| Task | Priority | Est. Time | Status |
|------|----------|-----------|--------|
| Deploy to Railway/Render | 🔴 High | 2 hr | ⬜ |
| Configure environment variables | 🔴 High | 1 hr | ⬜ |
| Test with GUVI Endpoint Tester | 🔴 High | 2 hr | ⬜ |
| Fix any issues | 🔴 High | 4 hr | ⬜ |
| Load testing | 🟡 Med | 2 hr | ⬜ |
| Submit solution | 🔴 High | 30 min | ⬜ |

### Phase 7: Buffer & Polish (Day 13-14)
> **Goal:** Handle edge cases and optimize

| Task | Priority | Est. Time | Status |
|------|----------|-----------|--------|
| Handle edge cases | 🟡 Med | 4 hr | ⬜ |
| Improve response quality | 🟡 Med | 3 hr | ⬜ |
| Optimize response time | 🟡 Med | 2 hr | ⬜ |
| Documentation | 🟢 Low | 2 hr | ⬜ |
| Final testing | 🔴 High | 3 hr | ⬜ |

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- Redis (optional, can use in-memory dict)
- Google Cloud account (for Gemini API) or OpenAI API key

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd honey-pot
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
```

**.env file:**
```env
# API Configuration
API_KEY=your-secret-api-key-here
PORT=8000

# Google Gemini API (Get from https://aistudio.google.com/apikey)
GEMINI_API_KEY=your-gemini-api-key

# Redis Configuration (optional - can use in-memory)
REDIS_URL=redis://localhost:6379

# GUVI Callback
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult

# Agent Configuration
MODEL_NAME=gemini-2.5-flash
MAX_CONVERSATION_TURNS=20
```

### 5. Run Locally

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Or run with ADK dev tools (for agent debugging)
adk web --port 8080

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Test API

```bash
# Health check
curl http://localhost:8000/health

# Test scam detection
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-secret-api-key-here" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Share OTP now!",
      "timestamp": "2026-01-27T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

---

## 📚 API Documentation

Once running, access interactive docs at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/analyze` | Main honeypot endpoint |

---

## ☁️ Deployment

### Option 1: Railway (Recommended)

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Create new project → Deploy from GitHub
4. Add environment variables
5. Deploy!

```bash
# Railway CLI (optional)
npm install -g @railway/cli
railway login
railway init
railway up
```

### Option 2: Render

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service
4. Connect GitHub repo
5. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy!

### Option 3: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t honeypot .
docker run -p 8000:8000 --env-file .env honeypot
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Tests

```bash
# API tests
pytest tests/test_api.py -v

# Detection tests
pytest tests/test_detector.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Manual Testing Script

```bash
python scripts/test_local.py
```

---

## 📊 Dependencies

**requirements.txt:**
```
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
python-dotenv==1.0.0

# Google ADK & Gemini
google-adk>=0.2.0
google-genai>=1.0.0

# HTTP Client
httpx==0.26.0

# Session Storage (optional)
redis==5.0.1

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
```

---

## 🏗️ Architecture: ADK Agent Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HONEYPOT AGENT ARCHITECTURE (ADK)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    SequentialAgent: HoneypotPipeline             │    │
│  │                                                                   │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │    │
│  │  │  LlmAgent:   │    │  LlmAgent:   │    │  LlmAgent:   │       │    │
│  │  │  Detector    │───▶│  Honeypot    │───▶│  Extractor   │       │    │
│  │  │              │    │  Persona     │    │              │       │    │
│  │  └──────────────┘    └──────────────┘    └──────────────┘       │    │
│  │        │                    │                    │               │    │
│  │        ▼                    ▼                    ▼               │    │
│  │  output_key:          output_key:          output_key:          │    │
│  │  'scam_analysis'      'agent_response'     'intelligence'       │    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Tools Available:                                                        │
│  ├── extract_bank_accounts()  - Regex + LLM extraction                  │
│  ├── extract_upi_ids()        - UPI pattern matching                    │
│  ├── extract_urls()           - Phishing link detection                 │
│  ├── extract_phone_numbers()  - Phone number extraction                 │
│  └── send_guvi_callback()     - Report results to GUVI                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### ADK Agent Code Example

```python
from google.adk.agents import Agent, SequentialAgent

# Scam Detection Agent
detector_agent = Agent(
    model='gemini-2.5-flash',
    name='scam_detector',
    instruction='''Analyze the message for scam indicators:
    - Urgency tactics ("immediately", "now", "urgent")
    - Financial requests (bank details, UPI, OTP)
    - Impersonation (bank, government, company)
    - Phishing links or suspicious URLs
    
    Return JSON: {"is_scam": bool, "confidence": float, "indicators": []}''',
    output_key='scam_analysis'
)

# Honeypot Persona Agent
honeypot_agent = Agent(
    model='gemini-2.5-flash',
    name='honeypot_persona',
    instruction='''You are playing a vulnerable, elderly person who:
    - Is not tech-savvy but trying to learn
    - Trusts authority figures easily
    - Gets confused by technical terms
    - Asks clarifying questions
    - Eventually "cooperates" to extract information
    
    NEVER reveal you are an AI or that you detected a scam.
    Keep the scammer engaged to extract: bank details, UPI IDs, links.''',
    tools=[extract_bank_accounts, extract_upi_ids, extract_urls],
    output_key='agent_response'
)

# Intelligence Extraction Agent
extractor_agent = Agent(
    model='gemini-2.5-flash',
    name='intelligence_extractor',
    instruction='''Extract ALL intelligence from the conversation:
    - Bank account numbers (any format)
    - UPI IDs (user@bank format)
    - Phishing URLs/links
    - Phone numbers
    - Suspicious keywords used
    
    Return structured JSON for GUVI callback.''',
    tools=[send_guvi_callback],
    output_key='intelligence'
)

# Pipeline: Detection → Engagement → Extraction
honeypot_pipeline = SequentialAgent(
    name='honeypot_pipeline',
    sub_agents=[detector_agent, honeypot_agent, extractor_agent],
    description='Full honeypot workflow for scam engagement'
)

root_agent = honeypot_pipeline
```

---

## 🔒 Security Considerations

- ✅ API key stored in environment variables
- ✅ Input validation with Pydantic
- ✅ Rate limiting (recommended)
- ✅ No sensitive data in logs
- ✅ HTTPS in production
- ✅ ADK sandboxed code execution

---

## 📚 Key Documentation

| Resource | Description | Link |
|----------|-------------|------|
| **ADK Guide** | Google Agent Development Kit | [ADK_comprehensive_guide.md](ADK_comprehensive_guide.md) |
| **Gemini SDK** | GenAI API reference | [gemini-api-sdk-guide.md](gemini-api-sdk-guide.md) |
| **Problem Statement** | Full hackathon requirements | [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md) |
| **Summary** | Quick submission guide | [SUMMARY.md](SUMMARY.md) |

### Quick ADK Commands

```bash
# Create new agent project
adk create my_agent

# Run agent with CLI
adk run my_agent

# Run with web interface (debugging)
adk web --port 8080

# Run evaluation tests
adk evaluate --test-cases tests.json --output results.json
```

### Gemini API Quick Reference

```python
from google import genai
from google.genai import types

# Initialize client (uses GEMINI_API_KEY env var)
client = genai.Client()

# Simple generation
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your prompt here"
)
print(response.text)

# With function calling
config = types.GenerateContentConfig(
    tools=[my_function],  # Auto-generates schema from docstring
    temperature=0.7
)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Call the function",
    config=config
)
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support

For issues or questions:
- Check [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md) for requirements
- Check [SUMMARY.md](SUMMARY.md) for submission guide
- Open an issue on GitHub

---

**Built with ❤️ for HCL-GUVI Buildathon 2026**
