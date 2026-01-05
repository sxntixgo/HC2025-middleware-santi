# X-Forwarded-For IP Bypass

A web application with IP-based access control. The admin panel is only accessible from localhost. Can you bypass the IP check?

## Difficulty

Easy

## How to Run

```bash
cd challenge-1
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **Main Page:** http://localhost:8001/
- **Admin Endpoint:** http://localhost:8001/admin
- **Debug Endpoint:** http://localhost:8001/debug
