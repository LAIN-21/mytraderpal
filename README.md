# MyTraderPal

A trading journal application for tracking trades, strategies, and market observations.

## Quick Start

```bash
git clone <repository-url>
cd mytraderpal
make install
make start
```

Application runs at:
- Frontend: http://localhost:3000
- Backend: http://localhost:9000

**Prerequisites:** Docker Desktop installed and running

## Commands

```bash
make test      # Run tests
make logs      # View logs
make stop      # Stop containers
```

## Production Deployment

**Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID` (required)
- `AWS_SECRET_ACCESS_KEY` (required)

**CI/CD:** Push to `main` branch - deployment is automatic.

## Environment Files

**Created automatically by `make install`:**

- `src/app/.env` - Backend (local development)
  - `TABLE_NAME=mtp_app`
  - `DEV_MODE=true`
  - `AWS_REGION=us-east-1`

- `src/frontend-react/.env` - Frontend (local development)
  - `VITE_API_URL=http://localhost:9000`
  - `VITE_AWS_REGION=us-east-1`
  - `VITE_USER_POOL_ID=` (optional for local)
  - `VITE_USER_POOL_CLIENT_ID=` (optional for local)

## License

MIT
