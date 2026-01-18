# =============================================================================
# AI STRATEGY HUB - NGINX DOCKERFILE (Reverse Proxy)
# =============================================================================
# Dockerfile per il servizio Nginx reverse proxy in produzione
#
# Autore: Claude per Davide
# Data: 2026-01-18
# =============================================================================

FROM nginx:1.25-alpine

# Installa certificati SSL e utilities
RUN apk add --no-cache \
    certbot \
    certbot-nginx \
    openssl \
    curl

# Rimuovi configurazione default
RUN rm /etc/nginx/conf.d/default.conf

# Copia configurazione Nginx personalizzata
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/ 2>/dev/null || true

# Crea directory per logs e cache
RUN mkdir -p /var/log/nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx /var/cache/nginx

# Crea directory per SSL certificates
RUN mkdir -p /etc/letsencrypt /var/www/certbot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Esponi porte HTTP e HTTPS
EXPOSE 80 443

# Comando di avvio
CMD ["nginx", "-g", "daemon off;"]
