# Quick Start Guide

Get MyTraderPal running in under 2 minutes!

## Prerequisites

- **Docker Desktop** installed and running
- **Make** (pre-installed on macOS/Linux, or install via `brew install make`)

## Setup Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mytraderpal
```

### 2. Install and Start

```bash
# Install dependencies and setup environment
make install

# Start the application
make start
```

That's it! 🎉

## Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:9000
- **Health Check**: http://localhost:9000/v1/health

## Verify Everything Works

```bash
# Check if services are running
make verify
```

## Common Commands

```bash
make start    # Start containers
make stop     # Stop containers
make restart  # Restart containers
make logs     # View logs
make verify   # Verify services
make clean    # Clean up (removes volumes)
```

## Troubleshooting

### Docker Not Running
```
Error: Docker is not running
```
**Solution**: Start Docker Desktop

### Port Already in Use
```
Error: port 3000 or 9000 is already in use
```
**Solution**: 
- Stop the service using the port
- Or change ports in `docker-compose.yml`

### Environment File Missing
```
Warning: .env file not found
```
**Solution**: Run `make install` to create it automatically

### Containers Won't Start
```bash
# Check logs for errors
make logs

# Clean and restart
make clean
make start
```

## What Happens During Setup?

1. **`make install`**:
   - Checks Docker is installed and running
   - Creates `.env` file from template
   - Validates prerequisites

2. **`make start`**:
   - Builds Docker images (installs dependencies)
   - Starts frontend and backend containers
   - Sets up hot reloading for development

## Next Steps

- Open http://localhost:3000 in your browser
- Start developing! Changes auto-reload
- Check the [README.md](README.md) for more details

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Run `make help` for all available commands
- View logs with `make logs`
