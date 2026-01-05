# X-User-Role Header Bypass

A web application with role-based access control. The admin panel requires admin privileges. Can you escalate your permissions?

## Difficulty

Easy

## How to Run

```bash
cd challenge-2
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **Main Page:** http://localhost:8002/
- **Admin Endpoint:** http://localhost:8002/admin
- **Debug Endpoint:** http://localhost:8002/debug
