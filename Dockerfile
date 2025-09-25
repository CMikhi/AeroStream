###############################
# Builder Stage
###############################
FROM node:22-alpine AS builder

WORKDIR /app/backend

# Copy only backend package manifests first for caching
COPY backend/package*.json ./

# Install all dependencies (dev included for build)
RUN npm ci

# Copy backend source
COPY backend/ .

# Build the NestJS application (outputs to dist/)
RUN npm run build

###############################
# Production Stage
###############################
FROM node:22-alpine AS production

ENV NODE_ENV=production \
    PORT=8000

WORKDIR /app/backend

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy package manifests then install production deps only
COPY backend/package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

# Copy built application
COPY --from=builder /app/backend/dist ./dist

# Copy entrypoint script from repository root
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT}/ || exit 1

ENTRYPOINT ["dumb-init", "/app/docker-entrypoint.sh"]
CMD ["node", "dist/main.js"]