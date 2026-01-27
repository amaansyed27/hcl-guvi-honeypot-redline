# 🍯 Agentic Honey-Pot for Scam Detection & Intelligence Extraction

> HCL-GUVI Buildathon Jan-Feb 2026 | AI for Fraud Detection & User Safety

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered honeypot system that detects scam messages, autonomously engages scammers through believable conversations, and extracts actionable intelligence.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)

---

## Overview

This project implements an autonomous AI honeypot that:
- 🎯 **Detects** scam/fraudulent messages in real-time
- 🤖 **Engages** scammers with believable AI personas  
- 🎭 **Maintains** human-like multi-turn conversations
- 🔍 **Extracts** intelligence (bank accounts, UPI IDs, phishing links, phone numbers)
- 📊 **Reports** results to GUVI evaluation endpoint

---

## ✨ Features

### Scam Detection
- Real-time analysis using Gemini 2.5 Flash
- Detects: Bank fraud, UPI fraud, phishing, tech support scams, lottery scams
- Confidence scoring and indicator extraction

### Honeypot Personas
- **Elderly Person** - Kamala Devi, 68yo retired teacher (default)
- **Young Professional** - Rahul, 26yo software developer  
- **Worried Parent** - Priya, 45yo mother

### Intelligence Extraction
- Bank account numbers (regex + LLM)
- UPI IDs (user@bank format)
- Phone numbers (Indian format)
- Phishing URLs
- Scam keywords and tactics

### Auto-Reporting
- Automatic callback to GUVI endpoint when:
  - 5+ messages exchanged
  - High-confidence scam detected
  - Intelligence extracted

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Language** | Python 3.11+ | Core application |
| **LLM** | Google Gemini 2.5 Flash | AI responses via `google-genai` SDK |
| **API Framework** | FastAPI | REST API with async support |
| **Validation** | Pydantic v2 | Request/response models |
| **HTTP Client** | httpx | GUVI callback requests |
| **Testing** | pytest + pytest-asyncio | Unit & integration tests |

### Why Gemini 2.5 Flash?
- ⚡ **Fast** - Low latency for real-time conversations
- 🧠 **Smart** - Excellent at maintaining personas
- 💰 **Free Tier** - 60 RPM, 1M tokens/day
- 🔧 **Simple SDK** - `google-genai` is straightforward

---

## 📁 Project Structure

```
honeypot/
├── app/
│   ├── agents/                 # AI Agent modules
│   │   ├── scam_detector.py    # Scam detection logic
│   │   ├── honeypot_persona.py # Persona response generation
│   │   ├── intelligence_extractor.py # Intel extraction
│   │   └── __init__.py
│   ├── api/
│   │   ├── routes.py           # API endpoints
│   │   ├── middleware.py       # Auth middleware
│   │   └── __init__.py
│   ├── models/
│   │   ├── request.py          # Request schemas
│   │   ├── response.py         # Response schemas
│   │   └── intelligence.py     # Intelligence models
│   ├── prompts/
│   │   ├── detection.py        # Scam detection prompts
│   │   ├── persona.py          # Persona prompts
│   │   └── extraction.py       # Extraction prompts
│   ├── services/
│   │   ├── gemini.py           # Gemini API wrapper
│   │   └── session.py          # Session management
│   ├── tools/
│   │   ├── extraction.py       # Regex extraction
│   │   └── callback.py         # GUVI callback
│   ├── config.py               # Settings
│   └── main.py                 # FastAPI app
├── scripts/
│   ├── test_local.py           # Local testing script
│   └── simulate_scammer.py     # Scam simulation
├── tests/
│   ├── test_api.py             # API tests
│   └── test_extraction.py      # Extraction tests
├── docs/
│   ├── PROBLEM_STATEMENT.md    # Original requirements
│   └── gemini-api-sdk-guide.md # Gemini SDK reference
├── .env.example                # Environment template
├── Dockerfile                  # Container config
├── requirements.txt            # Dependencies
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone <repository-url>
cd hcl-guvi-buidathon-jan-feb-2026

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
```

**.env file:**
```env
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
MODEL_NAME=gemini-2.5-flash
API_KEY=your_api_key_for_auth
GUVI_CALLBACK_URL=https://guvi.in/api/buildathon/scamhoneypot
DEBUG=true
```

Get your Gemini API key from: https://aistudio.google.com/apikey

### 3. Run the Server

```bash
# Development
python -m uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Test the API

```bash
python scripts/test_local.py
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication
All endpoints require `x-api-key` header:
```
x-api-key: your_api_key
```

### Endpoints

#### `POST /api/analyze`
Main honeypot endpoint - analyzes messages and generates responses.

**Request:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your account is blocked! Send OTP to verify@paytm",
    "timestamp": "2026-01-27T10:00:00Z"
  },
  "conversationHistory": []
}
```

**Response:**
```json
{
  "status": "success",
  "scamDetected": true,
  "agentResponse": "Oh my god! My account is blocked? But I just withdrew money yesterday. What should I do?",
  "engagementMetrics": {
    "engagementDurationSeconds": 45,
    "totalMessagesExchanged": 2
  },
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": ["verify@paytm"],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": ["blocked", "OTP", "verify"]
  },
  "agentNotes": "Bank fraud scam using urgency and fear tactics. UPI ID extracted."
}
```

#### `GET /api/session/{session_id}`
Get session details.

#### `DELETE /api/session/{session_id}`
End a session and trigger final callback.

#### `GET /api/health`
Health check endpoint.

### Interactive Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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

# Extraction tests
pytest tests/test_extraction.py -v
```

### Local Integration Test
```bash
python scripts/test_local.py
```

### Simulate Scammer Conversation
```bash
python scripts/simulate_scammer.py
```

---

## 🐳 Deployment

### Docker

```bash
# Build
docker build -t honeypot-api .

# Run
docker run -p 8000:8000 --env-file .env honeypot-api
```

### Railway / Render

1. Connect your GitHub repository
2. Set environment variables:
   - `GOOGLE_API_KEY`
   - `API_KEY`
   - `GUVI_CALLBACK_URL`
3. Deploy!

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ | - | Gemini API key |
| `MODEL_NAME` | ❌ | `gemini-2.5-flash` | Model to use |
| `API_KEY` | ❌ | `honeypot-secret-key` | API authentication |
| `GUVI_CALLBACK_URL` | ❌ | - | GUVI callback endpoint |
| `DEBUG` | ❌ | `false` | Enable debug logging |

---

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    HONEYPOT FLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. RECEIVE MESSAGE                                              │
│     └── Scammer sends message via /api/analyze                   │
│                                                                  │
│  2. DETECT SCAM (scam_detector.py)                              │
│     ├── Analyze message with Gemini                              │
│     ├── Check for scam indicators                                │
│     └── Return: is_scam, confidence, type, indicators            │
│                                                                  │
│  3. GENERATE RESPONSE (honeypot_persona.py)                     │
│     ├── Select persona (elderly, professional, parent)           │
│     ├── Build conversation context                               │
│     ├── Generate believable response with Gemini                 │
│     └── Return: persona response that keeps scammer engaged      │
│                                                                  │
│  4. EXTRACT INTELLIGENCE (intelligence_extractor.py)            │
│     ├── Regex extraction (bank accounts, UPI, phones, URLs)      │
│     ├── LLM extraction (context-aware)                           │
│     └── Merge and deduplicate                                    │
│                                                                  │
│  5. UPDATE SESSION                                               │
│     ├── Store message history                                    │
│     ├── Track engagement metrics                                 │
│     └── Merge intelligence                                       │
│                                                                  │
│  6. CALLBACK (if conditions met)                                │
│     ├── 5+ messages AND scam detected AND intelligence found     │
│     └── POST to GUVI callback endpoint                           │
│                                                                  │
│  7. RETURN RESPONSE                                              │
│     └── JSON with scamDetected, agentResponse, intelligence      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏆 Evaluation Criteria

Based on GUVI Buildathon requirements:

| Criteria | Weight | Our Implementation |
|----------|--------|-------------------|
| Scam Detection Accuracy | 25% | Gemini-powered detection with confidence scoring |
| Persona Believability | 25% | Multiple personas with natural Hindi-English mix |
| Intelligence Extraction | 25% | Regex + LLM hybrid approach |
| Engagement Duration | 15% | Multi-turn conversation handling |
| API Response Quality | 10% | Proper schema, error handling, logging |

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👥 Team

HCL-GUVI Buildathon Jan-Feb 2026

---

## 🙏 Acknowledgments

- Google Gemini API for LLM capabilities
- FastAPI for the excellent web framework
- GUVI for organizing the buildathon
