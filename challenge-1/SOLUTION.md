# Solution: X-Forwarded-For IP Bypass

## Overview

This challenge demonstrates a vulnerability where an application trusts the `X-Forwarded-For` header to determine the client's IP address without proper validation. The application restricts admin access to localhost (127.0.0.1), but this can be bypassed by injecting a forged `X-Forwarded-For` header.

## Step 1: Reconnaissance

First, attempt to access the admin endpoint directly:

```bash
curl http://localhost:8001/admin
```

This returns an "Access Denied" message, confirming that the endpoint is protected by IP-based access control.

## Step 2: Information Gathering

Use the debug endpoint to see how the application processes request headers:

```bash
curl http://localhost:8001/debug
```

This displays all request headers received by the Flask application, including any headers added by nginx.

## Step 3: Vulnerability Identification

The application checks the `X-Forwarded-For` header to determine the client's IP address. Reverse proxies typically use this header to preserve the original client IP when forwarding requests.

The vulnerability exists because:
1. The application trusts the `X-Forwarded-For` header completely
2. nginx passes this header through without sanitization
3. No validation occurs to ensure the header value is legitimate

## Step 4: Exploitation

Inject an `X-Forwarded-For` header with the value `127.0.0.1` to spoof your IP address as localhost:

```bash
curl -H "X-Forwarded-For: 127.0.0.1" http://localhost:8001/admin
```

The application will:
1. Read the `X-Forwarded-For` header value
2. Compare it against the allowed IP (`127.0.0.1`)
3. Grant access because the spoofed IP matches

## Step 5: Flag Retrieval

The successful request returns the flag in the response body.
