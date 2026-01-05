# Solution: X-Original-URL Path Bypass

## Overview

This challenge demonstrates a vulnerability where an application uses the `X-Original-URL` header for internal routing, allowing attackers to bypass path-based restrictions implemented at the reverse proxy level. While nginx blocks direct access to `/admin`, the Flask application can be tricked into routing to this endpoint via header manipulation.

## Step 1: Reconnaissance

First, attempt to access the admin endpoint directly:

```bash
curl http://localhost:8004/admin
```

This returns a 403 Forbidden error from nginx, confirming that the reverse proxy is blocking access to admin paths.

## Step 2: Exploring Available Endpoints

Access the public endpoint, which is allowed:

```bash
curl http://localhost:8004/public
```

This returns a message about the public area. Check the debug endpoint to understand how requests are processed:

```bash
curl http://localhost:8004/debug
```

## Step 3: Vulnerability Identification

The application's `/public` endpoint contains logic that checks for an `X-Original-URL` header. This header is sometimes used by reverse proxies to preserve the original requested URL after URL rewriting.

The vulnerability exists because:
1. nginx blocks direct requests to `/admin` paths
2. nginx allows requests to `/public`
3. The Flask application's `/public` endpoint reads the `X-Original-URL` header
4. If present, it internally routes to the path specified in that header
5. This bypasses nginx's path-based restrictions entirely

## Step 4: Exploitation

Send a request to the allowed `/public` endpoint with an `X-Original-URL` header pointing to the restricted `/admin` endpoint:

```bash
curl -H "X-Original-URL: /admin" http://localhost:8004/public
```

The application flow:
1. nginx receives a request to `/public` (allowed)
2. nginx forwards the request with the `X-Original-URL` header intact
3. Flask's `/public` handler detects the header
4. Flask internally routes to `/admin` using the header value
5. The admin endpoint logic executes and returns the flag

You can verify this behavior by checking what headers are being processed:

```bash
curl -H "X-Original-URL: /admin" http://localhost:8004/debug
```

## Step 5: Flag Retrieval

The successful request returns the flag in JSON format, demonstrating that the internal routing bypassed nginx's path restrictions.
