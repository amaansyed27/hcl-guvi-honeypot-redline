"""
Local Testing Script

Run this script to test the honeypot API locally.
"""

import requests
import json
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"  # Change to your actual API key

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}


def test_health():
    """Test health endpoint."""
    print("\n" + "="*50)
    print("Testing Health Endpoint")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_scam_detection():
    """Test scam detection with a typical scam message."""
    print("\n" + "="*50)
    print("Testing Scam Detection")
    print("="*50)
    
    payload = {
        "sessionId": f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "message": {
            "sender": "scammer",
            "text": "URGENT: Your SBI account will be blocked today! Share OTP immediately to verify. Call +919999888877",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        json=payload,
        headers=HEADERS
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_multi_turn_conversation():
    """Test multi-turn conversation handling."""
    print("\n" + "="*50)
    print("Testing Multi-Turn Conversation")
    print("="*50)
    
    session_id = f"multi-turn-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Turn 1: Initial scam message
    turn1 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Hello, I am calling from SBI bank. Your account has been flagged for suspicious activity.",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
    }
    
    print("Turn 1:")
    print(f"Scammer: {turn1['message']['text']}")
    
    response1 = requests.post(f"{BASE_URL}/api/analyze", json=turn1, headers=HEADERS)
    result1 = response1.json()
    
    print(f"Honeypot: {result1.get('agentResponse', 'No response')}")
    print(f"Scam Detected: {result1.get('scamDetected')}")
    
    # Turn 2: Follow-up with UPI request
    turn2 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "To verify your identity, please transfer Rs. 1 to verify@ybl and share the OTP you receive.",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "conversationHistory": [
            turn1["message"],
            {
                "sender": "user",
                "text": result1.get("agentResponse", ""),
                "timestamp": datetime.now().isoformat() + "Z"
            }
        ],
        "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
    }
    
    print("\nTurn 2:")
    print(f"Scammer: {turn2['message']['text']}")
    
    response2 = requests.post(f"{BASE_URL}/api/analyze", json=turn2, headers=HEADERS)
    result2 = response2.json()
    
    print(f"Honeypot: {result2.get('agentResponse', 'No response')}")
    print(f"Intelligence: {json.dumps(result2.get('extractedIntelligence', {}), indent=2)}")
    
    return response1.status_code == 200 and response2.status_code == 200


def test_session_endpoints():
    """Test session management endpoints."""
    print("\n" + "="*50)
    print("Testing Session Endpoints")
    print("="*50)
    
    # Create a session via analyze
    session_id = f"session-test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Your account is blocked. Send money to scammer@upi",
            "timestamp": datetime.now().isoformat() + "Z"
        },
        "conversationHistory": []
    }
    
    # Create session
    requests.post(f"{BASE_URL}/api/analyze", json=payload, headers=HEADERS)
    
    # Get session
    print(f"\nGetting session: {session_id}")
    response = requests.get(f"{BASE_URL}/api/session/{session_id}", headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Session: {json.dumps(response.json(), indent=2)}")
    
    # Delete session
    print(f"\nDeleting session: {session_id}")
    response = requests.delete(f"{BASE_URL}/api/session/{session_id}", headers=HEADERS)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "#"*60)
    print("# HONEYPOT API LOCAL TESTING")
    print("#"*60)
    
    results = {
        "Health Check": test_health(),
        "Scam Detection": test_scam_detection(),
        "Multi-Turn Conversation": test_multi_turn_conversation(),
        "Session Endpoints": test_session_endpoints()
    }
    
    print("\n" + "="*50)
    print("TEST RESULTS")
    print("="*50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("🎉 All tests passed!" if all_passed else "⚠️ Some tests failed"))
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()
