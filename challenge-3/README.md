# HTTP Method Override Bypass

A web application with method-based access control. Direct GET requests to the admin endpoint are blocked. Can you find an alternative approach?

## Difficulty

Medium

## How to Run

```bash
cd challenge-3
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **Main Page:** http://localhost:8003/
- **Admin Endpoint:** http://localhost:8003/admin
- **Debug Endpoint:** http://localhost:8003/debug
