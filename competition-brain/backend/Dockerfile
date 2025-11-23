# Competition Brain Backend - Production Dockerfile

FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3001

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 expressjs

# Copy dependencies
COPY --from=deps --chown=expressjs:nodejs /app/node_modules ./node_modules

# Copy application code
COPY --chown=expressjs:nodejs ./src ./src
COPY --chown=expressjs:nodejs package.json ./

# Create cache directory
RUN mkdir -p .cache && chown expressjs:nodejs .cache

USER expressjs

EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3001/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["npm", "start"]
