"""
Mock Scammer Simulator

Simulates scammer behavior for testing the honeypot system.
"""

import requests
import json
import time
from datetime import datetime
import random


# Configuration
HONEYPOT_URL = "http://localhost:8000/api/analyze"
API_KEY = "your-secret-api-key-here"  # Change to your actual API key

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}


# Scam message templates
SCAM_SCENARIOS = {
    "bank_fraud": {
        "opening": [
            "URGENT: Your SBI account has been flagged for suspicious activity. Call immediately.",
            "This is a notification from HDFC Bank. Your account will be blocked in 24 hours.",
            "ICICI Bank Alert: Your debit card has been used for Rs. 49,999. If not you, call now."
        ],
        "escalation": [
            "Sir, your account is being used for money laundering. Police complaint will be filed.",
            "Your account will be permanently blocked if you don't verify within 1 hour.",
            "This is the last warning. Complete KYC immediately or face legal action."
        ],
        "extraction": [
            "For verification, please share your account number and OTP.",
            "Transfer Rs. 1 to our verification account {upi_id} to confirm your identity.",
            "Share your card number and CVV for security verification."
        ]
    },
    "upi_fraud": {
        "opening": [
            "Congratulations! You have won Rs. 50,000 cashback. Claim now!",
            "Your PhonePe/GPay is selected for Rs. 10,000 reward. Click to claim.",
            "Special offer: Get 100% cashback on your next transaction!"
        ],
        "escalation": [
            "Offer expires in 10 minutes! Act now to claim your reward.",
            "Only 3 rewards remaining. Don't miss this opportunity!",
            "Your reward will be cancelled if not claimed immediately."
        ],
        "extraction": [
            "Send Rs. 99 to activate your reward to {upi_id}",
            "Share your UPI PIN to complete verification and receive Rs. 50,000.",
            "Click this link to claim: http://fake-reward.xyz/claim"
        ]
    },
    "tech_support": {
        "opening": [
            "Microsoft Security Alert: Your computer has been hacked. Call support now.",
            "Warning: Virus detected on your device. Download our security app immediately.",
            "Your WhatsApp will be blocked due to policy violation. Verify now."
        ],
        "escalation": [
            "Hackers are stealing your data right now. We need remote access to fix this.",
            "Your personal photos and files are at risk. Act immediately!",
            "This is your final warning before we report to cyber police."
        ],
        "extraction": [
            "Download TeamViewer and share the ID: teamviewer.com/download",
            "Pay Rs. 2,999 for premium security protection to {upi_id}",
            "Share your OTP to verify and protect your account."
        ]
    }
}

UPI_IDS = [
    "scammer@ybl",
    "verify@paytm", 
    "secure@gpay",
    "refund@okaxis",
    "support@upi"
]


class MockScammer:
    """Simulates a scammer in conversation."""
    
    def __init__(self, scenario_type: str = "bank_fraud"):
        self.scenario = SCAM_SCENARIOS.get(scenario_type, SCAM_SCENARIOS["bank_fraud"])
        self.upi_id = random.choice(UPI_IDS)
        self.turn = 0
        self.session_id = f"scam-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        self.conversation_history = []
        
    def get_message(self) -> str:
        """Get the next scam message based on conversation stage."""
        if self.turn == 0:
            messages = self.scenario["opening"]
        elif self.turn < 3:
            messages = self.scenario["escalation"]
        else:
            messages = self.scenario["extraction"]
        
        message = random.choice(messages)
        # Replace placeholders
        message = message.replace("{upi_id}", self.upi_id)
        
        return message
    
    def send_message(self, honeypot_response: str = None) -> dict:
        """Send a message to the honeypot and get response."""
        
        # Add previous honeypot response to history if exists
        if honeypot_response:
            self.conversation_history.append({
                "sender": "user",
                "text": honeypot_response,
                "timestamp": datetime.now().isoformat() + "Z"
            })
        
        # Get new scam message
        scam_message = self.get_message()
        
        payload = {
            "sessionId": self.session_id,
            "message": {
                "sender": "scammer",
                "text": scam_message,
                "timestamp": datetime.now().isoformat() + "Z"
            },
            "conversationHistory": self.conversation_history,
            "metadata": {
                "channel": "WhatsApp",
                "language": "English",
                "locale": "IN"
            }
        }
        
        print(f"\n{'='*60}")
        print(f"SCAMMER [Turn {self.turn + 1}]: {scam_message}")
        print("="*60)
        
        try:
            response = requests.post(HONEYPOT_URL, json=payload, headers=HEADERS)
            result = response.json()
            
            honeypot_reply = result.get("agentResponse", "")
            
            print(f"\nHONEYPOT: {honeypot_reply}")
            print(f"\nScam Detected: {result.get('scamDetected')}")
            print(f"Intelligence: {json.dumps(result.get('extractedIntelligence', {}), indent=2)}")
            
            # Add to conversation history
            self.conversation_history.append({
                "sender": "scammer",
                "text": scam_message,
                "timestamp": datetime.now().isoformat() + "Z"
            })
            
            self.turn += 1
            
            return {
                "scam_message": scam_message,
                "honeypot_response": honeypot_reply,
                "result": result
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def run_simulation(self, num_turns: int = 5):
        """Run a full scam simulation."""
        print("\n" + "#"*60)
        print(f"# SCAM SIMULATION - {self.session_id}")
        print(f"# Scenario: {list(SCAM_SCENARIOS.keys())[0]}")
        print(f"# UPI ID: {self.upi_id}")
        print("#"*60)
        
        honeypot_response = None
        
        for i in range(num_turns):
            result = self.send_message(honeypot_response)
            
            if result:
                honeypot_response = result["honeypot_response"]
            else:
                print("Simulation stopped due to error")
                break
            
            # Add delay between turns
            time.sleep(2)
        
        print("\n" + "#"*60)
        print("# SIMULATION COMPLETE")
        print(f"# Total Turns: {self.turn}")
        print(f"# Session ID: {self.session_id}")
        print("#"*60)


def run_multiple_scenarios():
    """Run multiple scam scenarios."""
    scenarios = ["bank_fraud", "upi_fraud", "tech_support"]
    
    for scenario in scenarios:
        print(f"\n\n{'*'*70}")
        print(f"* Running Scenario: {scenario.upper()}")
        print("*"*70)
        
        scammer = MockScammer(scenario_type=scenario)
        scammer.run_simulation(num_turns=4)
        
        time.sleep(3)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        scenario = sys.argv[1]
        turns = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        scammer = MockScammer(scenario_type=scenario)
        scammer.run_simulation(num_turns=turns)
    else:
        # Run bank fraud scenario by default
        scammer = MockScammer(scenario_type="bank_fraud")
        scammer.run_simulation(num_turns=5)
