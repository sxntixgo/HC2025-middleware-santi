# Solution: X-User-Role Header Bypass

## Overview

This challenge demonstrates a vulnerability where an application uses a custom HTTP header (`X-User-Role`) to determine user authorization without any server-side authentication. Since HTTP headers can be arbitrarily set by the client, this creates a trivial privilege escalation vulnerability.

## Step 1: Reconnaissance

First, attempt to access the admin endpoint directly:

```bash
curl http://localhost:8002/admin
```

This returns a "User Role Not Included" error with HTTP 401, indicating that the application expects some form of role information.

## Step 2: Information Gathering

Use the debug endpoint to see what headers the application receives:

```bash
curl http://localhost:8002/debug
```

This shows all request headers being processed by the application. Notice that there are no special authentication headers by default.

## Step 3: Vulnerability Identification

The application relies solely on the `X-User-Role` header for authorization. This is a critical security flaw because:
1. HTTP headers are entirely controlled by the client
2. There is no authentication mechanism to verify the user's identity
3. The header is not stripped or validated by the reverse proxy
4. Any client can claim to be an admin by simply setting this header

## Step 4: Exploitation

Inject an `X-User-Role` header with the value `admin` to escalate privileges:

```bash
curl -H "X-User-Role: admin" http://localhost:8002/admin
```

The application will:
1. Read the `X-User-Role` header value
2. Compare it against the required role (`admin`)
3. Grant access because the injected header matches

You can verify this works by checking the debug endpoint with the header:

```bash
curl -H "X-User-Role: admin" http://localhost:8002/debug
```

## Step 5: Flag Retrieval

The successful request to the admin endpoint returns the flag in the response body.
