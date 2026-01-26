"""
Intelligence Extraction Tests
"""

import pytest
from app.tools.extraction import (
    extract_bank_accounts,
    extract_upi_ids,
    extract_phone_numbers,
    extract_urls,
    extract_suspicious_keywords,
    extract_all_intelligence
)


class TestBankAccountExtraction:
    """Tests for bank account extraction."""
    
    def test_extract_simple_account(self):
        """Extract simple account number."""
        result = extract_bank_accounts("Transfer to account 123456789012")
        assert "123456789012" in result["bank_accounts"]
    
    def test_extract_formatted_account(self):
        """Extract account with dashes."""
        result = extract_bank_accounts("Account: 1234-5678-9012-3456")
        assert len(result["bank_accounts"]) >= 1
    
    def test_extract_account_with_prefix(self):
        """Extract account with 'a/c' prefix."""
        result = extract_bank_accounts("a/c no: 9876543210123")
        assert "9876543210123" in result["bank_accounts"]
    
    def test_no_false_positives(self):
        """Should not extract short numbers."""
        result = extract_bank_accounts("Call me at 12345")
        assert len(result["bank_accounts"]) == 0


class TestUPIExtraction:
    """Tests for UPI ID extraction."""
    
    def test_extract_simple_upi(self):
        """Extract standard UPI ID."""
        result = extract_upi_ids("Send to rahul@upi")
        assert "rahul@upi" in result["upi_ids"]
    
    def test_extract_paytm_upi(self):
        """Extract Paytm UPI ID."""
        result = extract_upi_ids("Pay to merchant@paytm")
        assert "merchant@paytm" in result["upi_ids"]
    
    def test_extract_bank_upi(self):
        """Extract bank-specific UPI ID."""
        result = extract_upi_ids("UPI: user.name@okhdfcbank")
        assert "user.name@okhdfcbank" in result["upi_ids"]
    
    def test_extract_multiple_upis(self):
        """Extract multiple UPI IDs."""
        result = extract_upi_ids("Send to scammer@ybl or alt@gpay")
        assert len(result["upi_ids"]) >= 2


class TestPhoneNumberExtraction:
    """Tests for phone number extraction."""
    
    def test_extract_indian_mobile(self):
        """Extract Indian mobile number."""
        result = extract_phone_numbers("Call +919876543210")
        assert "+919876543210" in result["phone_numbers"]
    
    def test_extract_10_digit(self):
        """Extract 10-digit number."""
        result = extract_phone_numbers("Contact: 9876543210")
        assert "+919876543210" in result["phone_numbers"]
    
    def test_extract_formatted_number(self):
        """Extract formatted number."""
        result = extract_phone_numbers("Call 98765-43210")
        assert len(result["phone_numbers"]) >= 1


class TestURLExtraction:
    """Tests for URL extraction."""
    
    def test_extract_http_url(self):
        """Extract HTTP URL."""
        result = extract_urls("Click http://example.com/verify")
        assert len(result["urls"]) >= 1
    
    def test_extract_https_url(self):
        """Extract HTTPS URL."""
        result = extract_urls("Visit https://secure-bank.com/login")
        assert len(result["urls"]) >= 1
    
    def test_extract_suspicious_domain(self):
        """Extract suspicious domain."""
        result = extract_urls("Download from malicious.xyz/app")
        assert len(result["urls"]) >= 1


class TestSuspiciousKeywords:
    """Tests for keyword detection."""
    
    def test_detect_urgency(self):
        """Detect urgency keywords."""
        result = extract_suspicious_keywords("Act immediately or face consequences")
        assert "immediately" in result["keywords"]
    
    def test_detect_financial(self):
        """Detect financial keywords."""
        result = extract_suspicious_keywords("Your bank account is blocked")
        assert "bank" in result["keywords"]
        assert "account" in result["keywords"]
        assert "blocked" in result["keywords"]
    
    def test_detect_verification(self):
        """Detect verification keywords."""
        result = extract_suspicious_keywords("Verify your KYC now")
        assert "verify" in result["keywords"]
        assert "kyc" in result["keywords"]


class TestCombinedExtraction:
    """Tests for combined extraction."""
    
    def test_extract_all_from_scam_message(self):
        """Extract all intelligence from realistic scam message."""
        message = """
        URGENT: Your SBI account 12345678901234 will be blocked today!
        To verify, send Rs. 1 to verify@ybl and share OTP.
        Call +919999888877 or visit http://sbi-verify.tk/kyc
        """
        
        intel = extract_all_intelligence(message)
        
        assert len(intel.bankAccounts) >= 1
        assert len(intel.upiIds) >= 1
        assert len(intel.phoneNumbers) >= 1
        assert len(intel.phishingLinks) >= 1
        assert "urgent" in intel.suspiciousKeywords
        assert "blocked" in intel.suspiciousKeywords
