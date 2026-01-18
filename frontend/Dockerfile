# =============================================================================
# AI STRATEGY HUB - FRONTEND DOCKERFILE (Next.js)
# =============================================================================
# Dockerfile per il servizio frontend Next.js in produzione
#
# Autore: Claude per Davide
# Data: 2026-01-18
# =============================================================================

# Stage 1: Dependencies - Installa tutte le dipendenze
FROM node:20-alpine AS deps

WORKDIR /app

# Installa dipendenze necessarie per node-gyp
RUN apk add --no-cache libc6-compat

# Copia package files
COPY package.json package-lock.json* ./

# Installa dipendenze
RUN npm ci --only=production && \
    npm cache clean --force

# -----------------------------------------------------------------------------
# Stage 2: Builder - Build dell'applicazione Next.js
# -----------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copia dipendenze dallo stage precedente
COPY --from=deps /app/node_modules ./node_modules

# Copia source code
COPY . .

# Build Next.js application
# NOTA: Se usi variabili ambiente al build time, passale qui
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Runner - Immagine finale production
# -----------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app

# Variabili ambiente
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

# Installa dumb-init per proper signal handling
RUN apk add --no-cache dumb-init

# Crea user non-root
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copia file necessari per runtime
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Setta ownership
RUN chown -R nextjs:nodejs /app

# Switch a user non-root
USER nextjs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Esponi porta Next.js
EXPOSE 3000

# Comando di avvio con dumb-init per proper signal handling
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
