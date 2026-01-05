# Duplicate Host Header Bypass

An advanced challenge involving HTTP Host header manipulation. The application validates the Host header for admin access. Can you satisfy multiple validation checks simultaneously?

## Difficulty

Hard

## How to Run

```bash
cd challenge-x
docker-compose -f docker-compose-dev.yml up --build
```

### Stopping the Challenge

```bash
docker-compose -f docker-compose-dev.yml down
```

## Accessing the Challenge

- **Main Page:** https://localhost:8443/
- **Admin Endpoint:** https://localhost:8443/admin
- **Debug Endpoint:** https://localhost:8443/debug

**Note:** This challenge uses HTTPS. Use the `-k` flag with curl to skip certificate validation for localhost.
