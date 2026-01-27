# 🎯 HCL-GUVI Buildathon: Agentic Honey-Pot - Project Summary

> **Theme:** AI for Fraud Detection & User Safety  
> **Problem:** Agentic Honey-Pot for Scam Detection & Intelligence Extraction

---

## 📅 Timeline

| Stage | Start Date | End Date | Status |
|-------|------------|----------|--------|
| Problem Selection | 17 Jan 2026, 01:15 PM | 05 Feb 2026, 11:59 PM | ✅ Qualified |
| API Endpoint Submission | 25 Jan 2026, 12:00 AM | 05 Feb 2026, 11:59 PM | 🟡 Active |

**⏰ Final Deadline: February 5, 2026, 11:59 PM**

---

## ✅ Implementation Status

### Core Features - COMPLETE ✅

| Feature | Status | Implementation |
|---------|--------|----------------|
| REST API Endpoint | ✅ Done | FastAPI with `/api/analyze` endpoint |
| API Key Auth | ✅ Done | `x-api-key` header middleware |
| Scam Detection | ✅ Done | Gemini 2.5 Flash powered detection |
| Honeypot Agent | ✅ Done | Multiple personas (elderly, professional, parent) |
| Multi-turn Conversations | ✅ Done | Session management with history |
| Intelligence Extraction | ✅ Done | Regex + LLM hybrid approach |
| GUVI Callback | ✅ Done | Auto-reports when conditions met |

### Scam Types Supported ✅

- Bank Fraud (account blocked, KYC, etc.)
- UPI Fraud (fake payment requests)
- Phishing (malicious links)
- Tech Support Scams
- Lottery/Prize Scams
- Government Impersonation (RBI, Income Tax, etc.)

### Intelligence Extracted ✅

- Bank Account Numbers
- UPI IDs (user@bank format)
- Phone Numbers (Indian format)
- Phishing URLs
- Scam Keywords & Tactics

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.11+ |
| **LLM** | Google Gemini 2.5 Flash |
| **SDK** | `google-genai` (simple, direct API) |
| **Framework** | FastAPI |
| **Validation** | Pydantic v2 |
| **HTTP Client** | httpx |

---

## 📁 Project Structure

```
honeypot/
├── app/
│   ├── agents/                 # AI modules
│   │   ├── scam_detector.py    # Scam detection
│   │   ├── honeypot_persona.py # Persona responses
│   │   └── intelligence_extractor.py
│   ├── api/
│   │   ├── routes.py           # API endpoints
│   │   └── middleware.py       # Auth
│   ├── models/                 # Pydantic schemas
│   ├── prompts/                # LLM prompts
│   ├── services/
│   │   ├── gemini.py           # Gemini wrapper
│   │   └── session.py          # Session mgmt
│   ├── tools/
│   │   ├── extraction.py       # Regex extraction
│   │   └── callback.py         # GUVI callback
│   ├── config.py
│   └── main.py
├── scripts/
│   ├── test_local.py
│   └── simulate_scammer.py
├── tests/
├── .env
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add GOOGLE_API_KEY

# Run
python -m uvicorn app.main:app --reload --port 8000

# Test
python scripts/test_local.py
```

---

## 📊 API Request/Response

### Request
```json
POST /api/analyze
Headers: x-api-key: your_key

{
  "sessionId": "unique-id",
  "message": {
    "sender": "scammer",
    "text": "Your account blocked! Send OTP to verify@paytm",
    "timestamp": "2026-01-27T10:00:00Z"
  },
  "conversationHistory": []
}
```

### Response
```json
{
  "status": "success",
  "scamDetected": true,
  "agentResponse": "Oh my god! My account? What happened?",
  "engagementMetrics": {
    "engagementDurationSeconds": 45,
    "totalMessagesExchanged": 2
  },
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": ["verify@paytm"],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": ["blocked", "OTP"]
  },
  "agentNotes": "Bank fraud using urgency tactics."
}
```

---

## 🏆 Evaluation Criteria Met

| Criteria | Weight | Implementation |
|----------|--------|----------------|
| Scam Detection | 25% | ✅ Gemini-powered with confidence scores |
| Persona Believability | 25% | ✅ 3 personas with Hindi-English mix |
| Intelligence Extraction | 25% | ✅ Regex + LLM hybrid |
| Engagement Duration | 15% | ✅ Multi-turn session tracking |
| API Quality | 10% | ✅ Proper schema, error handling |

---

## 📝 Key Decisions

### Why `google-genai` instead of ADK?

| Factor | google-genai | ADK |
|--------|-------------|-----|
| Complexity | Simple, direct | Complex, many abstractions |
| Setup | 1 line: `genai.Client()` | Requires Runner, SessionService, etc. |
| Control | Full control over prompts | Framework manages prompts |
| Reliability | Stable, well-documented | API changes, less docs |

### Architecture

1. **Scam Detector** - Analyzes messages, returns is_scam + confidence + type
2. **Honeypot Persona** - Generates believable responses
3. **Intelligence Extractor** - Regex (fast) + LLM (context-aware)
4. **Session Manager** - Tracks conversation state
5. **GUVI Callback** - Auto-reports when 5+ messages + scam + intel

---

## 🔗 Links

- **Swagger UI:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health
- **Gemini API:** https://aistudio.google.com/apikey
