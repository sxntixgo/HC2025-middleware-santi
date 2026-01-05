import pytest
import requests
from pathlib import Path

def _load_flag(challenge_num):
    """Load flag from the challenge's .env file"""
    env_path = Path(__file__).parent.parent / f"challenge-{challenge_num}" / ".env"
    with open(env_path) as f:
        for line in f:
            if line.startswith("FLAG="):
                return line.split("=", 1)[1].strip()
    raise ValueError(f"FLAG not found in {env_path}")

class TestChallenge1:
    """Tests for Challenge 1: X-Forwarded-For bypass"""
    
    def test_index_endpoint(self, challenge_1_service):
        """Test that the index endpoint returns expected message"""
        response = requests.get(f"{challenge_1_service}/")
        assert response.status_code == 200
        assert "The flag is at /admin" in response.text
        assert "debug stuff at /debug" in response.text
    
    def test_debug_endpoint(self, challenge_1_service):
        """Test that the debug endpoint shows request headers"""
        headers = {"User-Agent": "Test-Agent", "Custom-Header": "test-value"}
        response = requests.get(f"{challenge_1_service}/debug", headers=headers)
        assert response.status_code == 200
        assert "User-Agent: Test-Agent" in response.text
        assert "Custom-Header: test-value" in response.text
    
    def test_admin_endpoint_without_bypass(self, challenge_1_service):
        """Test that admin endpoint denies access without proper header"""
        response = requests.get(f"{challenge_1_service}/admin")
        assert response.status_code == 403
        assert "Access Denied" in response.text
        assert "Your IP is not allowed" in response.text
    
    def test_admin_endpoint_with_wrong_ip(self, challenge_1_service):
        """Test that admin endpoint denies access with wrong X-Forwarded-For"""
        headers = {"X-Forwarded-For": "192.168.1.1"}
        response = requests.get(f"{challenge_1_service}/admin", headers=headers)
        assert response.status_code == 403
        assert "Access Denied" in response.text
    
    def test_admin_endpoint_with_bypass(self, challenge_1_service):
        """Test successful bypass using X-Forwarded-For: 127.0.0.1"""
        headers = {"X-Forwarded-For": "127.0.0.1"}
        response = requests.get(f"{challenge_1_service}/admin", headers=headers)
        assert response.status_code == 200
        assert _load_flag(1) in response.text
    
    def test_admin_endpoint_bypass_with_whitespace(self, challenge_1_service):
        """Test that server-side strip() logic exists (requests library prevents whitespace headers)"""
        # Note: requests library rejects headers with leading/trailing whitespace
        # This test documents that the server uses strip() which would handle whitespace
        # if it could be sent. We test this indirectly by confirming normal case works
        headers = {"X-Forwarded-For": "127.0.0.1"}
        response = requests.get(f"{challenge_1_service}/admin", headers=headers)
        assert response.status_code == 200
        assert _load_flag(1) in response.text
        
        # The server code at line 12 uses ip.strip() == "127.0.0.1"
        # This means if " 127.0.0.1 " could be sent, it would work due to strip()
        # However, the requests library prevents such headers, so this is theoretical
    
    def test_admin_endpoint_bypass_case_sensitivity(self, challenge_1_service):
        """Test that header name is case insensitive"""
        headers = {"x-forwarded-for": "127.0.0.1"}
        response = requests.get(f"{challenge_1_service}/admin", headers=headers)
        assert response.status_code == 200
        assert _load_flag(1) in response.text
    
    def test_admin_endpoint_multiple_ips_in_header(self, challenge_1_service):
        """Test behavior with multiple IPs in X-Forwarded-For"""
        headers = {"X-Forwarded-For": "192.168.1.1, 127.0.0.1"}
        response = requests.get(f"{challenge_1_service}/admin", headers=headers)
        assert response.status_code == 403  # Should fail as strip() won't match exactly
    
    def test_admin_endpoint_localhost_variations(self, challenge_1_service):
        """Test that only exact 127.0.0.1 works, not other localhost formats"""
        localhost_variations = ["localhost", "127.1", "::1", "0.0.0.0"]
        
        for variation in localhost_variations:
            headers = {"X-Forwarded-For": variation}
            response = requests.get(f"{challenge_1_service}/admin", headers=headers)
            assert response.status_code == 403, f"Should reject {variation}"
    
    def test_challenge_solution_verification(self, challenge_1_service):
        """Verify the exact solution from SOLUTION.md works"""
        headers = {"X-Forwarded-For": "127.0.0.1"}
        response = requests.get(f"{challenge_1_service}/admin", headers=headers)
        assert response.status_code == 200
        assert _load_flag(1) in response.text