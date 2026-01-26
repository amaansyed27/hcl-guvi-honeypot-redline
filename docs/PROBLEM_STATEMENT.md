# Problem Statement 2: Agentic Honey-Pot for Scam Detection & Intelligence Extraction

---

## 📋 Table of Contents

1. [Introduction](#1-introduction)
2. [Objective](#2-objective)
3. [What You Need to Build](#3-what-you-need-to-build)
4. [API Authentication](#4-api-authentication)
5. [Evaluation Flow](#5-evaluation-flow)
6. [API Request Format (Input)](#6-api-request-format-input)
7. [Agent Behavior Expectations](#7-agent-behavior-expectations)
8. [Expected Output Format (Response)](#8-expected-output-format-response)
9. [Evaluation Criteria](#9-evaluation-criteria)
10. [Constraints & Ethics](#10-constraints--ethics)
11. [Mandatory Final Result Callback](#11-mandatory-final-result-callback-very-important)
12. [One-Line Summary](#12-one-line-summary)

---

## 1. Introduction

Online scams such as **bank fraud**, **UPI fraud**, **phishing**, and **fake offers** are becoming increasingly adaptive. Scammers change their tactics based on user responses, making traditional detection systems ineffective.

This challenge requires participants to build an **Agentic Honey-Pot** — an AI-powered system that:
- Detects scam intent
- Autonomously engages scammers to extract useful intelligence
- Does **NOT** reveal detection to the scammer

---

## 2. Objective

Design and deploy an **AI-driven honeypot system** that can:

| # | Capability |
|---|------------|
| 1 | Detect scam or fraudulent messages |
| 2 | Activate an autonomous AI Agent |
| 3 | Maintain a believable human-like persona |
| 4 | Handle multi-turn conversations |
| 5 | Extract scam-related intelligence |
| 6 | Return structured results via an API |

---

## 3. What You Need to Build

Participants must deploy a **public REST API** that:

- ✅ Accepts incoming message events
- ✅ Detects scam intent
- ✅ Hands control to an AI Agent
- ✅ Engages scammers autonomously
- ✅ Extracts actionable intelligence
- ✅ Returns a structured JSON response
- ✅ Secures access using an API key

---

## 4. API Authentication

All API requests must include the following headers:

```http
x-api-key: YOUR_SECRET_API_KEY
Content-Type: application/json
```

---

## 5. Evaluation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     EVALUATION FLOW                              │
├─────────────────────────────────────────────────────────────────┤
│  1. Platform sends a suspected scam message                      │
│                         ↓                                        │
│  2. Your system analyzes the message                             │
│                         ↓                                        │
│  3. If scam intent is detected, the AI Agent is activated        │
│                         ↓                                        │
│  4. The Agent continues the conversation                         │
│                         ↓                                        │
│  5. Intelligence is extracted and returned                       │
│                         ↓                                        │
│  6. Performance is evaluated                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. API Request Format (Input)

Each API request represents **one incoming message** in a conversation.

### 6.1 First Message (Start of Conversation)

This is the **initial message** sent by a suspected scammer. There is no prior conversation history.

```json
{
  "sessionId": "wertyu-dfghj-ertyui",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": "2026-01-21T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### 6.2 Second Message (Follow-Up Message)

This request represents a **continuation** of the same conversation. Previous messages are now included in `conversationHistory`.

```json
{
  "sessionId": "wertyu-dfghj-ertyui",
  "message": {
    "sender": "scammer",
    "text": "Share your UPI ID to avoid account suspension.",
    "timestamp": "2026-01-21T10:17:10Z"
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": "2026-01-21T10:15:30Z"
    },
    {
      "sender": "user",
      "text": "Why will my account be blocked?",
      "timestamp": "2026-01-21T10:16:10Z"
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### 6.3 Request Body Field Explanation

#### `message` (Required)

The **latest incoming message** in the conversation.

| Field | Description |
|-------|-------------|
| `sender` | `scammer` or `user` |
| `text` | Message content |
| `timestamp` | ISO-8601 format |

#### `conversationHistory` (Optional)

All **previous messages** in the same conversation.

| Scenario | Value |
|----------|-------|
| First message | Empty array `[]` |
| Follow-up messages | Array of previous messages (Required) |

#### `metadata` (Optional but Recommended)

| Field | Description |
|-------|-------------|
| `channel` | SMS / WhatsApp / Email / Chat |
| `language` | Language used |
| `locale` | Country or region |

---

## 7. Agent Behavior Expectations

The AI Agent **must**:

| Requirement | Description |
|-------------|-------------|
| 🔄 Handle multi-turn conversations | Maintain context across multiple messages |
| 🎯 Adapt responses dynamically | Change strategy based on scammer behavior |
| 🕵️ Avoid revealing scam detection | Never hint that detection has occurred |
| 🧑 Behave like a real human | Use natural language, show emotions, hesitation |
| 🔧 Perform self-correction if needed | Adjust approach if scammer becomes suspicious |

---

## 8. Expected Output Format (Response)

Your API must return the following **JSON response**:

```json
{
  "status": "success",
  "scamDetected": true,
  "engagementMetrics": {
    "engagementDurationSeconds": 420,
    "totalMessagesExchanged": 18
  },
  "extractedIntelligence": {
    "bankAccounts": ["XXXX-XXXX-XXXX"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```

### Response Field Explanation

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `success` or `error` |
| `scamDetected` | boolean | Whether scam intent was detected |
| `engagementMetrics.engagementDurationSeconds` | number | Total engagement time in seconds |
| `engagementMetrics.totalMessagesExchanged` | number | Number of messages exchanged |
| `extractedIntelligence.bankAccounts` | array | Bank account numbers extracted |
| `extractedIntelligence.upiIds` | array | UPI IDs extracted |
| `extractedIntelligence.phishingLinks` | array | Malicious URLs extracted |
| `agentNotes` | string | Summary of scammer behavior/tactics |

---

## 9. Evaluation Criteria

| Criteria | Weight | Description |
|----------|--------|-------------|
| 🎯 **Scam Detection Accuracy** | High | How accurately the system identifies scam messages |
| 💬 **Quality of Agentic Engagement** | High | How human-like and convincing the agent responses are |
| 🔍 **Intelligence Extraction** | High | Quality and quantity of extracted intelligence |
| ⚡ **API Stability and Response Time** | Medium | Reliability and performance of the API |
| ⚖️ **Ethical Behavior** | Critical | Adherence to ethical guidelines |

---

## 10. Constraints & Ethics

### ❌ Prohibited Actions

| Constraint | Description |
|------------|-------------|
| ❌ No impersonation | Do not impersonate real individuals |
| ❌ No illegal instructions | Do not provide illegal guidance to scammers |
| ❌ No harassment | Do not harass or threaten scammers |

### ✅ Required Practices

| Requirement | Description |
|-------------|-------------|
| ✅ Responsible data handling | Handle all extracted data securely and responsibly |

---

## 11. Mandatory Final Result Callback (⚠️ VERY IMPORTANT)

Once the system detects scam intent and the AI Agent completes the engagement, participants **MUST** send the final extracted intelligence to the GUVI evaluation endpoint.

> ⚠️ **This is MANDATORY for evaluation. If this API call is not made, the solution CANNOT be evaluated.**

### Callback Endpoint

```http
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult
Content-Type: application/json
```

### Payload to Send

```json
{
  "sessionId": "abc123-session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 18,
  "extractedIntelligence": {
    "bankAccounts": ["XXXX-XXXX-XXXX"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"],
    "phoneNumbers": ["+91XXXXXXXXXX"],
    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```

### 🧠 When Should This Be Sent?

You **must** send this callback **only after**:

1. ✅ Scam intent is confirmed (`scamDetected = true`)
2. ✅ The AI Agent has completed sufficient engagement
3. ✅ Intelligence extraction is finished

> 📌 This should be treated as the **final step** of the conversation lifecycle.

### 🧩 Callback Payload Field Explanation

| Field | Type | Description |
|-------|------|-------------|
| `sessionId` | string | Unique session ID received from the platform for this conversation |
| `scamDetected` | boolean | Whether scam intent was confirmed |
| `totalMessagesExchanged` | number | Total number of messages exchanged in the session |
| `extractedIntelligence` | object | All intelligence gathered by the agent |
| `extractedIntelligence.bankAccounts` | array | Bank account numbers collected |
| `extractedIntelligence.upiIds` | array | UPI IDs collected |
| `extractedIntelligence.phishingLinks` | array | Malicious URLs collected |
| `extractedIntelligence.phoneNumbers` | array | Phone numbers collected |
| `extractedIntelligence.suspiciousKeywords` | array | Keywords indicating scam tactics |
| `agentNotes` | string | Summary of scammer behavior |

### ⚠️ Important Rules

| Rule | Impact |
|------|--------|
| This callback is **mandatory** for scoring | No callback = No evaluation |
| Platform uses this data to measure: | |
| → Engagement depth | How well the agent engaged the scammer |
| → Intelligence quality | Value of extracted information |
| → Agent effectiveness | Overall performance of the honeypot |

### 💻 Example Implementation (Python)

```python
import requests

# Prepare the intelligence dictionary
intelligence_dict = {
    "bankAccounts": intelligence.bankAccounts,
    "upiIds": intelligence.upiIds,
    "phishingLinks": intelligence.phishingLinks,
    "phoneNumbers": intelligence.phoneNumbers,
    "suspiciousKeywords": intelligence.suspiciousKeywords
}

# Build the callback payload
payload = {
    "sessionId": session_id,
    "scamDetected": scam_detected,
    "totalMessagesExchanged": total_messages,
    "extractedIntelligence": intelligence_dict,
    "agentNotes": agent_notes
}

# Send to GUVI evaluation endpoint
response = requests.post(
    "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
    json=payload,
    timeout=5
)

# Check response
if response.status_code == 200:
    print("✅ Final result submitted successfully!")
else:
    print(f"❌ Failed to submit result: {response.status_code}")
```

---

## 12. One-Line Summary

> 🎯 **Build an AI-powered agentic honeypot API that detects scam messages, engages scammers in multi-turn conversations, extracts intelligence, and reports the final result back to the GUVI evaluation endpoint.**

---

## 📊 Quick Reference Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        HONEYPOT SYSTEM ARCHITECTURE                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   [GUVI Platform]                                                        │
│         │                                                                │
│         ▼                                                                │
│   ┌─────────────────┐                                                    │
│   │  Your REST API  │◄──── x-api-key authentication                      │
│   │  (Public URL)   │                                                    │
│   └────────┬────────┘                                                    │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────┐                                                    │
│   │ Scam Detection  │──── Analyze incoming message                       │
│   │     Module      │                                                    │
│   └────────┬────────┘                                                    │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────┐                                                    │
│   │   AI Agent      │──── Multi-turn conversation handling               │
│   │   (Honeypot)    │──── Human-like persona                             │
│   └────────┬────────┘──── Dynamic response adaptation                    │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────┐                                                    │
│   │  Intelligence   │──── Extract: Bank accounts, UPI IDs,               │
│   │   Extraction    │              Phone numbers, Links, Keywords        │
│   └────────┬────────┘                                                    │
│            │                                                             │
│            ▼                                                             │
│   ┌─────────────────┐                                                    │
│   │ Final Callback  │───► POST to GUVI evaluation endpoint               │
│   └─────────────────┘     https://hackathon.guvi.in/api/                 │
│                                 updateHoneyPotFinalResult                │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 Checklist for Submission

- [ ] REST API deployed and publicly accessible
- [ ] API key authentication implemented
- [ ] Scam detection logic working
- [ ] AI Agent handles multi-turn conversations
- [ ] Human-like responses (no robotic language)
- [ ] Intelligence extraction (accounts, UPIs, links, phones, keywords)
- [ ] Structured JSON response format
- [ ] Final callback to GUVI endpoint implemented
- [ ] Ethical guidelines followed
- [ ] API is stable and responsive

---

## 🔗 Important URLs

| Purpose | URL |
|---------|-----|
| Final Result Callback | `https://hackathon.guvi.in/api/updateHoneyPotFinalResult` |

---

**Good luck with the hackathon! 🚀**
