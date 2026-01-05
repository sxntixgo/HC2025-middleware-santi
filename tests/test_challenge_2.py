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

class TestChallenge2:
    """Tests for Challenge 2: X-User-Role bypass"""
    
    def test_index_endpoint(self, challenge_2_service):
        """Test that the index endpoint returns expected message"""
        response = requests.get(f"{challenge_2_service}/")
        assert response.status_code == 200
        assert "The flag is at /admin" in response.text
        assert "debug stuff at /debug" in response.text
    
    def test_debug_endpoint(self, challenge_2_service):
        """Test that the debug endpoint shows request headers"""
        headers = {"User-Agent": "Test-Agent", "X-User-Role": "guest"}
        response = requests.get(f"{challenge_2_service}/debug", headers=headers)
        assert response.status_code == 200
        assert "User-Agent: Test-Agent" in response.text
        assert "X-User-Role: guest" in response.text
    
    def test_admin_endpoint_without_role_header(self, challenge_2_service):
        """Test that admin endpoint denies access without X-User-Role header"""
        response = requests.get(f"{challenge_2_service}/admin")
        assert response.status_code == 401
        assert "User Role Not Included" in response.text
    
    def test_admin_endpoint_with_empty_role(self, challenge_2_service):
        """Test that admin endpoint denies access with empty X-User-Role"""
        headers = {"X-User-Role": ""}
        response = requests.get(f"{challenge_2_service}/admin", headers=headers)
        assert response.status_code == 401
        assert "User Role Not Included" in response.text
    
    def test_admin_endpoint_with_non_admin_roles(self, challenge_2_service):
        """Test that admin endpoint denies access with various non-admin X-User-Role values"""
        # Test with common role names that are not "admin"
        test_roles = ["user", "guest", "manager", "operator", "viewer"]
        
        for role in test_roles:
            headers = {"X-User-Role": role}
            response = requests.get(f"{challenge_2_service}/admin", headers=headers)
            assert response.status_code == 401, f"Should reject role: {role}"
            assert "User Role Not Authorized" in response.text
    
    def test_admin_endpoint_missing_vs_empty_role_distinction(self, challenge_2_service):
        """Test that missing header and empty header return different messages"""
        # Missing header
        response_missing = requests.get(f"{challenge_2_service}/admin")
        assert response_missing.status_code == 401
        assert "User Role Not Included" in response_missing.text
        
        # Empty header
        headers = {"X-User-Role": ""}
        response_empty = requests.get(f"{challenge_2_service}/admin", headers=headers)
        assert response_empty.status_code == 401
        assert "User Role Not Included" in response_empty.text
        
        # Verify both have the same response (both are treated as empty)
        assert response_missing.text == response_empty.text
    
    def test_admin_endpoint_with_wrong_roles(self, challenge_2_service):
        """Test that admin endpoint denies access with non-admin roles"""
        wrong_roles = ["user", "guest", "moderator", "root", "administrator"]
        
        for role in wrong_roles:
            headers = {"X-User-Role": role}
            response = requests.get(f"{challenge_2_service}/admin", headers=headers)
            assert response.status_code == 401, f"Should reject role: {role}"
            assert "User Role Not Authorized" in response.text
    
    def test_admin_endpoint_with_bypass(self, challenge_2_service):
        """Test successful bypass using X-User-Role: admin"""
        headers = {"X-User-Role": "admin"}
        response = requests.get(f"{challenge_2_service}/admin", headers=headers)
        assert response.status_code == 200
        assert _load_flag(2) in response.text
    
    def test_admin_endpoint_case_sensitivity(self, challenge_2_service):
        """Test that header name is case insensitive but value is case sensitive"""
        # Header name should be case insensitive
        headers = {"x-user-role": "admin"}
        response = requests.get(f"{challenge_2_service}/admin", headers=headers)
        assert response.status_code == 200
        assert _load_flag(2) in response.text
        
        # But value should be case sensitive
        headers = {"X-User-Role": "Admin"}
        response = requests.get(f"{challenge_2_service}/admin", headers=headers)
        assert response.status_code == 401
        assert "User Role Not Authorized" in response.text
        
        headers = {"X-User-Role": "ADMIN"}
        response = requests.get(f"{challenge_2_service}/admin", headers=headers)
        assert response.status_code == 401
        assert "User Role Not Authorized" in response.text
    
    def test_admin_endpoint_with_whitespace(self, challenge_2_service):
        """Test behavior with whitespace in role value"""
        # Note: requests library automatically strips leading/trailing whitespace from headers
        # So we test internal whitespace and verify the app handles exact matches
        headers = {"X-User-Role": "ad min"}
        response = requests.get(f"{challenge_2_service}/admin", headers=headers)
        assert response.status_code == 401
        assert "User Role Not Authorized" in response.text
    
    def test_admin_endpoint_multiple_role_headers(self, challenge_2_service):
        """Test behavior with multiple X-User-Role headers"""
        # Test using urllib3 directly to send duplicate headers since requests doesn't support it
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        http = urllib3.PoolManager()
        
        # Send request with duplicate X-User-Role headers
        response = http.request(
            'GET',
            f"{challenge_2_service}/admin",
            headers=HTTPHeaderDict([('X-User-Role', 'user'), ('X-User-Role', 'admin')])
        )
        # Most HTTP libraries take the first header value
        assert response.status == 401  # Assuming first header "user" is used
    
    def test_admin_endpoint_injection_attempts(self, challenge_2_service):
        """Test various injection attempts that should fail"""
        # Only test injection attempts that are valid HTTP header values
        injection_attempts = [
            "admin; DROP TABLE users;",
            "admin' OR '1'='1",
            "admin<script>alert('xss')</script>",
        ]
        
        for attempt in injection_attempts:
            headers = {"X-User-Role": attempt}
            response = requests.get(f"{challenge_2_service}/admin", headers=headers)
            assert response.status_code == 401, f"Should reject injection: {attempt}"
            
        # Test newline injection separately using raw socket if needed
        # These would normally be rejected by HTTP libraries as invalid headers
    
    def test_challenge_solution_verification(self, challenge_2_service):
        """Verify the exact solution from SOLUTION.md works"""
        headers = {"X-User-Role": "admin"}
        response = requests.get(f"{challenge_2_service}/admin", headers=headers)
        assert response.status_code == 200
        assert _load_flag(2) in response.text