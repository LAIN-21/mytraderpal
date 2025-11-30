# Authentication Setup Guide

## Error: "Auth UserPool not configured"

This error occurs when AWS Cognito credentials are not set. You have two options:

## Option 1: Set Up Cognito (For Production/Full Features)

### Step 1: Get Your Cognito Credentials

1. Go to **AWS Console** → **Cognito** → **User Pools**
2. Select your user pool
3. Copy the **User Pool ID** (looks like: `us-east-1_ABC123XYZ`)
4. Go to **App integration** → **App clients**
5. Copy the **Client ID** (looks like: `1a2b3c4d5e6f7g8h9i0j`)

### Step 2: Create `.env` File

Create `src/frontend-react/.env`:

```env
VITE_API_URL=http://localhost:9000
VITE_USER_POOL_ID=us-east-1_ABC123XYZ
VITE_USER_POOL_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j
VITE_AWS_REGION=us-east-1
```

### Step 3: Restart Dev Server

```bash
# Stop the current server (Ctrl+C)
# Then restart
cd src/frontend-react
npm run dev
```

## Option 2: Run Without Auth (For Development/Testing)

If you just want to test the app without setting up Cognito:

### Backend: Use DEV_MODE

The backend already supports `DEV_MODE=true` which bypasses authentication.

### Frontend: No Action Needed

The frontend will now automatically allow access if Cognito is not configured (for development only).

**Note**: This is only for local development. For production, you must configure Cognito.

## Quick Setup Script

```bash
# Copy example file
cd src/frontend-react
cp .env.example .env

# Edit .env with your values
# Then restart dev server
npm run dev
```

## Troubleshooting

### Still Getting the Error?

1. **Check `.env` file exists**: `ls -la src/frontend-react/.env`
2. **Check variables are set**: `cat src/frontend-react/.env`
3. **Restart dev server**: Variables are only loaded at startup
4. **Check variable names**: Must start with `VITE_` prefix

### Variables Not Loading?

Vite only loads `.env` files from the project root (`src/frontend-react/`).

Make sure:
- File is named `.env` (not `.env.local` or `.env.development`)
- File is in `src/frontend-react/` directory
- Variables start with `VITE_` prefix
- Dev server was restarted after creating/editing `.env`

### For Docker

If running with Docker, pass environment variables as build args:

```yaml
# docker-compose.yml
frontend:
  build:
    args:
      - VITE_USER_POOL_ID=${VITE_USER_POOL_ID}
      - VITE_USER_POOL_CLIENT_ID=${VITE_USER_POOL_CLIENT_ID}
```

## Development Mode (No Auth Required)

If you're just developing and don't need authentication:

1. **Backend**: Already supports `DEV_MODE=true` (set in docker-compose.yml)
2. **Frontend**: Now automatically allows access if Cognito not configured

You can develop and test without setting up Cognito!


