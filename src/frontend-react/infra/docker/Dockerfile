# Frontend Dockerfile
# Supports both development (Vite dev server) and production (Nginx)
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code (will be overridden by volume mount for hot reload in dev)
COPY . .

# Expose port (3000 for dev server, 80 for production)
EXPOSE 3000

# Default to dev server (can be overridden in docker-compose)
CMD ["npm", "run", "dev"]

