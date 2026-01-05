# Solution: Duplicate Host Header Bypass

## Overview

This challenge demonstrates an advanced HTTP request smuggling technique using duplicate Host headers. The application validates the Host header for admin access, but when multiple Host headers are sent, Flask/Werkzeug combines them into a comma-separated string. This allows an attacker to satisfy multiple validation checks simultaneously.

## Step 1: Reconnaissance

First, attempt to access the admin endpoint with the default Host header:

```bash
curl -k https://localhost:8443/admin
```

This returns an error: "HTTP request domain verification failed. Expected: admin.local" with HTTP 403.

## Step 2: Testing Host Header Validation

Try accessing with the expected `admin.local` hostname:

```bash
curl -k -H "Host: admin.local" https://localhost:8443/admin
```

This returns a different error: "Invalid hostname. Server name indication (SNI) mismatch" with HTTP 421, indicating the application performs SNI validation.

## Step 3: Understanding the Validation Logic

Use the debug endpoint to understand how headers are processed:

```bash
curl -k https://localhost:8443/debug
```

The application performs two validations:
1. SNI validation - ensures the first Host value matches the expected hostname (localhost)
2. Domain validation - checks for `admin.local` in the Host header

## Step 4: Vulnerability Identification

The vulnerability exists because:
1. HTTP/1.1 technically allows multiple headers with the same name
2. Flask/Werkzeug combines duplicate Host headers into a comma-separated string
3. The application splits this string and validates each part separately
4. Different validation checks examine different parts of the split values

This creates an opportunity to satisfy both validations simultaneously.

## Step 5: Exploitation

Send a request with exactly two Host headers - first matching the server (localhost), second being `admin.local`:

```bash
curl -k -H "Host: localhost" -H "Host: admin.local" https://localhost:8443/admin
```

The application flow:
1. curl sends two separate Host headers
2. The WSGI server combines them: `localhost, admin.local`
3. The application splits on comma: `["localhost", "admin.local"]`
4. First validation checks `localhost` matches expected hostname ✓
5. Second validation finds `admin.local` in the array ✓
6. Both checks pass, granting access

You can verify the header processing by checking the debug endpoint:

```bash
curl -k -H "Host: localhost" -H "Host: admin.local" https://localhost:8443/debug
```

## Step 6: Flag Retrieval

The successful request returns the flag in the response body.

**Note:** The `-k` flag is required to skip SSL certificate validation for the self-signed localhost certificate.
