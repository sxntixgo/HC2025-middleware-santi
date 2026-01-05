# WAF Challenge Tests

This directory contains comprehensive tests for all five WAF bypass challenges. The tests verify both the expected vulnerable behavior and the defensive security aspects of each challenge.

## Quick Start

Run all tests:
```bash
./run_tests.sh
```

Run tests for a specific challenge:
```bash
./run_tests.sh 1  # Challenge 1 only
./run_tests.sh 2  # Challenge 2 only
./run_tests.sh 3  # Challenge 3 only
./run_tests.sh 4  # Challenge 4 only
./run_tests.sh x  # Challenge X only
```

## Test Structure

### Test Files
- `test_challenge_1.py` - X-Forwarded-For bypass tests
- `test_challenge_2.py` - X-User-Role bypass tests
- `test_challenge_3.py` - HTTP Method Override bypass tests
- `test_challenge_4.py` - X-Original-URL bypass tests
- `test_challenge_x.py` - Duplicate Host header bypass tests
- `conftest.py` - Shared test fixtures and configuration
- `pytest.ini` - Pytest configuration

### Test Coverage

Each test file covers:
- **Basic functionality** - Index and debug endpoints work correctly
- **Access control** - Admin endpoint properly denies unauthorized access
- **Bypass verification** - The documented bypass technique works
- **Edge cases** - Various input variations and attack attempts
- **Security validation** - Ensures only the intended bypass works

### Challenge 1 Tests (X-Forwarded-For)
- Verifies IP-based access control
- Tests various IP formats and whitespace handling
- Validates that only `127.0.0.1` bypasses the restriction
- Tests header case insensitivity
- Verifies multiple IP handling in X-Forwarded-For

### Challenge 2 Tests (X-User-Role)
- Verifies role-based access control
- Tests various role values and case sensitivity
- Validates that only `admin` role grants access
- Tests injection attempts and security boundaries
- Verifies header handling behavior

### Challenge 3 Tests (HTTP Method Override)
- Verifies method-based access control
- Tests GET vs POST authorization differences
- Validates X-HTTP-Method-Override header processing
- Tests authorization bypass via method spoofing
- Verifies privilege escalation prevention

### Challenge 4 Tests (X-Original-URL)
- Verifies path-based access control at proxy level
- Tests nginx blocking of admin paths
- Validates X-Original-URL header routing bypass
- Tests internal URL rewriting behavior
- Verifies reverse proxy security bypass

### Challenge X Tests (Duplicate Host Header)
- Verifies host-based access control
- Tests various hostname formats and variations
- Validates that duplicate Host headers enable bypass
- Tests SSL/TLS configuration
- Verifies SNI validation and dual-header processing
- Tests HTTP request smuggling techniques
- Validates boundary conditions and edge cases

## Manual Testing

For manual verification of the challenges:

### Challenge 1
```bash
curl -H "X-Forwarded-For: 127.0.0.1" http://localhost:8001/admin
```

### Challenge 2
```bash
curl -H "X-User-Role: admin" http://localhost:8002/admin
```

### Challenge 3
```bash
curl -X POST -H "X-HTTP-Method-Override: GET" http://localhost:8003/admin
```

### Challenge 4
```bash
curl -H "X-Original-URL: /admin" http://localhost:8004/public
```

### Challenge X
```bash
curl -k -H "Host: localhost" -H "Host: admin.local" https://localhost:8443/admin
```

## Requirements

- Docker and docker-compose
- Python 3.7+
- pip (for installing test dependencies)

The test runner script will automatically:
1. Create a Python virtual environment
2. Install required dependencies (pytest, requests)
3. Start and stop Docker services for each challenge
4. Run comprehensive test suites
5. Provide detailed results and cleanup

## Security Note

These tests verify that the challenges work as intended for **defensive security education**. The tests ensure that:
- The vulnerabilities are properly demonstrated
- Only the documented bypass techniques work
- The challenges maintain their educational value
- Security boundaries are properly tested

All challenges are designed to teach security professionals about common attack vectors that need to be defended against in production systems.
