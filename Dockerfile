# syntax=docker/dockerfile:1.6
# CivikSutra frontend image — multi-stage build so Cloud Build can produce
# a fully self-contained Cloud Run image without any local pre-build step.
#
#   1. ``frontend-build`` compiles the React/Vite SPA with strict typecheck.
#   2. ``runtime`` serves the static bundle through hardened Nginx on :8080.

# ---- Stage 1: build the production SPA bundle ------------------------------
FROM node:20-alpine AS frontend-build
WORKDIR /workspace
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --prefer-offline
COPY frontend/ ./
ENV CI=true
RUN npm run build

# ---- Stage 2: hardened Nginx serving the built bundle ----------------------
FROM nginx:1.27-alpine AS runtime
RUN apk add --no-cache curl tini && rm -rf /var/cache/apk/*
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /workspace/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --silent http://127.0.0.1:8080/ >/dev/null || exit 1
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["nginx", "-g", "daemon off;"]
