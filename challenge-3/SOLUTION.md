# Solution: HTTP Method Override Bypass

## Overview

This challenge demonstrates a vulnerability where an application implements inconsistent authorization checks across different HTTP methods. The `GET /admin` endpoint has proper authorization, but the `POST /admin` endpoint processes method override headers (`X-HTTP-Method-Override`) without performing authorization checks first.

## Step 1: Reconnaissance

First, attempt to access the admin endpoint using a GET request:

```bash
curl http://localhost:8003/admin
```

This returns an "Unauthorized" error with HTTP 403, confirming that direct GET access is properly protected.

## Step 2: Testing Different HTTP Methods

Try accessing the endpoint using a POST request:

```bash
curl -X POST http://localhost:8003/admin
```

This returns a different response indicating that POST requests are handled separately, with a message about the endpoint not being fully implemented.

## Step 3: Vulnerability Identification

The application accepts an `X-HTTP-Method-Override` header. This header is commonly used to work around client or network limitations by allowing clients to tunnel other HTTP methods through POST requests.

The vulnerability exists because:
1. The GET handler has proper authorization checks
2. The POST handler processes method override headers
3. The POST handler calls the admin logic directly without authorization when the override header is present
4. This creates an authorization bypass pathway

## Step 4: Exploitation

Send a POST request with the `X-HTTP-Method-Override` header set to `GET`:

```bash
curl -X POST -H "X-HTTP-Method-Override: GET" http://localhost:8003/admin
```

The application flow:
1. Receives a POST request to `/admin`
2. Checks for the `X-HTTP-Method-Override` header
3. Finds the header value is `GET`
4. Calls the internal admin logic function directly
5. Returns the flag without checking authorization

You can verify the header is being processed by checking the debug endpoint:

```bash
curl -X POST -H "X-HTTP-Method-Override: GET" http://localhost:8003/debug
```

## Step 5: Flag Retrieval

The successful POST request with the method override header returns the flag in JSON format.
