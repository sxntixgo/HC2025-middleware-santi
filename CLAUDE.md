# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a WAF (Web Application Firewall) bypass challenge repository containing four main cybersecurity challenges plus an advanced challenge designed to demonstrate various HTTP header manipulation techniques. Each challenge is a defensive security exercise showing common bypass methods that security professionals need to understand.

## Repository Structure

```
waf/
├── challenge-1/        # X-Forwarded-For bypass challenge
├── challenge-2/        # X-User-Role bypass challenge  
├── challenge-3/        # HTTP Method Override bypass challenge
├── challenge-4/        # X-Original-URL path bypass challenge
├── challenge-x/        # Host header bypass challenge (advanced)
├── tests/              # Comprehensive test suite
└── run_tests.sh        # Test runner script
```

Each challenge follows the same structure:
- `app.py` - Flask application with vulnerable endpoint (runs with Gunicorn WSGI server)
- `Dockerfile` - Container configuration with production-ready Gunicorn setup
- `docker-compose.yml` - Production configuration with nginx and certbot
- `docker-compose-dev.yml` - Development configuration
- `nginx.conf` - Reverse proxy configuration
- `SOLUTION.md` - Challenge solution explanation
- `.env` - Environment variables including challenge flag (used by both app and tests)

## Common Development Commands

### Running Individual Challenges

#### Development Mode
Navigate to any challenge directory and run:
```bash
docker-compose -f docker-compose-dev.yml up --build
```

#### Production Mode
Navigate to any challenge directory and run:
```bash
docker-compose up --build
```

Each challenge in production mode runs with nginx reverse proxy and certbot:
- Challenge 1-4: nginx on ports 80/443 (HTTP/HTTPS), proxying to Gunicorn WSGI server (port 5000)
- Challenge-x: Gunicorn with SSL directly on port 8443 (HTTPS only)

### Accessing Challenge Endpoints
- `/` - Instructions and debug endpoint info
- `/admin` - Protected endpoint containing the flag
- `/debug` - Shows all request headers (useful for testing)

### Running Tests
Run comprehensive test suite for all challenges:
```bash
./run_tests.sh
```

Run tests for specific challenge:
```bash
./run_tests.sh 1  # Challenge 1 only
./run_tests.sh 2  # Challenge 2 only
./run_tests.sh 3  # Challenge 3 only
./run_tests.sh 4  # Challenge 4 only
```

### Manual Testing
Use curl or similar tools to test header bypass techniques:
```bash
# Challenge 1: IP bypass
curl -H "X-Forwarded-For: 127.0.0.1" https://localhost/admin

# Challenge 2: Role bypass
curl -H "X-User-Role: admin" https://localhost/admin

# Challenge 3: Method override bypass
curl -X POST -H "X-HTTP-Method-Override: GET" https://localhost/admin

# Challenge 4: Path bypass via X-Original-URL
curl -H "X-Original-URL: /admin/flag" https://localhost/anything

# Challenge-x: Host header bypass (advanced)
curl -H "Host: localhost, admin.local" https://localhost:8443/admin
```

## Architecture Notes

### Challenge 1: X-Forwarded-For Bypass
- Tests IP-based access control bypass
- nginx preserves original X-Forwarded-For headers
- Flask checks X-Forwarded-For against 127.0.0.1

### Challenge 2: Role-Based Access Control
- Tests custom header injection
- Uses X-User-Role header for authorization
- No reverse proxy filtering of custom headers

### Challenge 3: HTTP Method Override Bypass
- Tests authorization bypass via X-HTTP-Method-Override
- GET /admin requires auth, but POST /admin processes method overrides without auth
- Demonstrates privilege escalation via method spoofing

### Challenge 4: X-Original-URL Path Bypass
- Tests path traversal via URL rewrite headers
- nginx blocks admin paths but Flask routes via X-Original-URL
- Demonstrates reverse proxy security control bypass

### Challenge-x: Host Header Attack (Advanced)
- Tests HTTP request smuggling via duplicate headers
- Gunicorn handles HTTPS with SSL termination using provided certificates
- Flask validates Host header against admin.local

## Security Context

This repository contains **defensive security challenges** designed for:
- Security training and education
- Understanding WAF bypass techniques
- Testing reverse proxy configurations
- Learning HTTP header manipulation defenses

All challenges demonstrate vulnerabilities that should be **prevented** in production systems. The solutions show attack vectors that security professionals need to defend against.

## Testing Infrastructure

### Test Suite Architecture
The comprehensive test suite (`tests/` directory) includes:
- **Dynamic Flag Loading**: Tests automatically read flags from each challenge's `.env` file
- **Comprehensive Coverage**: Tests for both positive and negative cases, edge cases, and security implications
- **Production-Ready**: Uses pytest with proper fixtures and realistic HTTP scenarios

### Challenge-Specific Test Coverage

#### Challenge 1-4: Core WAF Bypass Tests (70+ test cases)
- **X-Forwarded-For bypass**: IP spoofing and header manipulation
- **X-User-Role bypass**: Custom header injection and authorization bypass
- **HTTP Method Override**: Method spoofing and privilege escalation
- **X-Original-URL bypass**: Path traversal and URL rewrite attacks

#### Challenge-X: Advanced Host Header Attacks (26 test cases)
- **Host Header Parsing**: Edge cases, whitespace handling, case sensitivity
- **Duplicate Header Bypass**: Multiple Host headers, order dependency
- **Injection Attempts**: HTTP request smuggling, newline injection protection  
- **Boundary Conditions**: Exact requirement validation, error consistency
- **Security Features**: SSL/TLS validation, concurrent request handling
- **Performance Testing**: Response time benchmarking, resource usage validation

### Key Testing Features
- **Flag Verification**: Tests dynamically load and verify flags from `.env` files using `_load_flag()` helper functions
- **Header Manipulation Testing**: Comprehensive tests for various header injection techniques
- **SSL/TLS Testing**: Full HTTPS testing for challenge-x with certificate validation
- **Edge Case Coverage**: Tests for malformed requests, injection attempts, and boundary conditions
- **Security Validation**: Ensures bypass techniques work as intended for educational purposes
- **Comprehensive Challenge-X Coverage**: 26+ test cases covering Host header attacks, concurrency, performance, and security boundaries
- **Attack Vector Testing**: HTTP request smuggling, Host header injection, boundary conditions, and bypass variations
- **Security Boundary Validation**: Information leakage prevention, error response consistency, SSL security features

### Test Execution
```bash
# Run all tests (includes all challenges 1-4 + X)
./run_tests.sh

# Run specific challenge tests
./run_tests.sh 1        # Challenge 1 only
./run_tests.sh 2        # Challenge 2 only  
./run_tests.sh 3        # Challenge 3 only
./run_tests.sh 4        # Challenge 4 only
./run_tests.sh x        # Challenge X only (comprehensive Host header tests)

# Manual pytest execution
pytest tests/test_challenge_1.py -v
pytest tests/test_challenge_x.py -v  # Comprehensive Host header attack tests

# Run specific test categories
pytest tests/test_challenge_x.py::TestChallengeX::test_host_header_parsing_edge_cases -v
pytest tests/test_challenge_x.py::TestChallengeX::test_security_bypass_variations -v

# Manual service startup (if needed)
cd challenge-1 && docker-compose -f docker-compose-dev.yml up -d
cd challenge-x && docker-compose up -d  # Uses different compose file
```

### Educational Test Categories

#### Security Attack Vector Testing
```bash
# Host header injection and parsing edge cases
pytest tests/test_challenge_x.py::TestChallengeX::test_host_header_injection_attempts -v

# HTTP request smuggling protection
pytest tests/test_challenge_x.py::TestChallengeX::test_admin_endpoint_boundary_conditions -v

# Method override security implications
pytest tests/test_challenge_3.py::TestChallenge3::test_method_override_security_bypass_demonstration -v

# Path traversal via header manipulation
pytest tests/test_challenge_4.py::TestChallenge4::test_original_url_bypass_admin_flag -v
```

#### Performance and Reliability Testing
```bash
# Concurrent request handling
pytest tests/test_challenge_x.py::TestChallengeX::test_concurrent_requests_behavior -v

# SSL/TLS security validation
pytest tests/test_challenge_x.py::TestChallengeX::test_ssl_security_features -v

# Response time benchmarking
pytest tests/test_challenge_x.py::TestChallengeX::test_performance_and_resource_usage -v
```

## Production Deployment

### WSGI Server Configuration
All challenges now use **Gunicorn** as the production WSGI server:
- **Performance**: 4 worker processes for concurrent request handling
- **Security**: Production-ready server instead of Flask development server
- **SSL Support**: Native SSL/TLS termination in challenge-x
- **Logging**: Proper production logging without development warnings

### Deployment Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   nginx (80/443)│ -> │  Gunicorn:5000  │ -> │  Flask App      │
│   Reverse Proxy │    │  WSGI Server    │    │  (Vulnerable)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ^                       ^                       ^
    SSL/TLS               4 Workers              Flag from .env
   Termination           Production             Security Logic
                         Ready
```

### Environment Configuration
Each challenge uses `.env` files for configuration:
- **Flag Storage**: `FLAG=HC{challenge_specific_flag}`
- **Dynamic Loading**: Both applications and tests read from the same source
- **Maintainability**: Easy flag updates without code changes

## Recent Improvements

### v2024.1 Updates
1. **Production WSGI Server**: Migrated from Flask development server to Gunicorn
2. **Dynamic Flag Loading**: Tests now read flags from `.env` files instead of hardcoded values  
3. **Enhanced SSL Support**: Proper certificate handling in challenge-x
4. **Improved Logging**: Production-ready logging without development warnings
5. **Better Documentation**: Updated architecture notes and deployment guidance

### v2024.2 Updates (Latest)
1. **Comprehensive Challenge-X Testing**: Added 15+ additional test cases covering advanced Host header attacks
2. **Security Boundary Testing**: Enhanced validation for injection attempts, concurrency, and performance
3. **Test Infrastructure Fixes**: Fixed challenge 3 & 4 test failures, updated header validation handling
4. **Advanced Attack Vector Coverage**: HTTP request smuggling, boundary conditions, bypass variations
5. **SSL/TLS Security Validation**: Certificate handling, HTTPS enforcement, and security feature testing
6. **Test Runner Enhancement**: Updated `./run_tests.sh` to include challenge-x support with `./run_tests.sh x`

### Test Coverage Enhancements
- **Challenge-X Test Suite**: Expanded from 11 to 26 comprehensive test cases
- **Attack Vector Categories**: Host header parsing, injection attempts, boundary conditions
- **Security Validation**: Error response consistency, information leakage prevention
- **Performance Testing**: Concurrent request handling, response time benchmarking
- **Edge Case Coverage**: Special characters, Unicode support, malformed header handling

### Benefits Achieved
- ✅ **Production Ready**: No more Flask development server warnings
- ✅ **Better Performance**: 4 worker processes for handling concurrent requests  
- ✅ **Enhanced Security**: Proper WSGI server with SSL support
- ✅ **Test Maintainability**: Dynamic flag loading from environment files
- ✅ **Deployment Stability**: More robust request handling for security testing
- ✅ **Comprehensive Security Testing**: 100+ total test cases across all challenges
- ✅ **Advanced Attack Coverage**: Host header attacks, HTTP method override, path traversal
- ✅ **Educational Value**: Complete attack vector documentation for security professionals

## Summary of Enhancements

### Complete WAF Bypass Challenge Suite
This repository now provides a comprehensive educational platform for understanding web application firewall bypasses with:

- **5 Production-Ready Challenges** running on Gunicorn WSGI servers
- **100+ Test Cases** covering all major HTTP header manipulation techniques  
- **Advanced Security Testing** including Host header attacks, method overrides, and path traversal
- **Real-World Attack Scenarios** demonstrating actual bypass techniques used by security professionals
- **Defensive Learning** showing both attack vectors and proper prevention methods

### Professional Security Training Features
- **Realistic Production Environment**: Nginx reverse proxy + Gunicorn + SSL/TLS
- **Comprehensive Attack Vector Coverage**: All common WAF bypass techniques
- **Security Boundary Testing**: Injection attempts, error handling, information disclosure prevention
- **Performance Validation**: Concurrent request handling and response time benchmarking
- **Educational Documentation**: Complete attack explanations and defensive countermeasures

This enhanced platform serves as an excellent resource for security professionals, penetration testers, and developers learning about web application security vulnerabilities and their prevention.