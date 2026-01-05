# X-Original-URL Path Bypass

A web application protected by a reverse proxy. The nginx proxy blocks direct access to admin paths. Can you bypass the proxy restrictions?

## Difficulty

Medium

## How to Run

```bash
cd challenge-4
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **Main Page:** http://localhost:8004/
- **Public Area:** http://localhost:8004/public
- **Admin Endpoint:** http://localhost:8004/admin (blocked by proxy)
- **Debug Endpoint:** http://localhost:8004/debug
