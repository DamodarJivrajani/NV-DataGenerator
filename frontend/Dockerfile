# syntax=docker/dockerfile:1

# ---- Build stage: compile the Vite/React app to static assets ----
FROM node:20-alpine AS build
WORKDIR /app

# Install from the lockfile for reproducible, deterministic builds.
COPY package.json package-lock.json ./
RUN npm ci

# Vite runs in production mode here and loads .env.production
# (VITE_API_URL=/api/v1), so the SPA calls the API same-origin and nginx
# proxies those calls to the backend.
COPY . .
RUN npm run build

# ---- Serve stage: nginx serving the SPA + proxying /api/v1 to the backend ----
FROM nginx:alpine

# Built static assets
COPY --from=build /app/dist /usr/share/nginx/html

# nginx config delivered as a template: the official image runs envsubst over
# /etc/nginx/templates/*.template at startup, substituting ${BACKEND_URL}
# (provided as a Cloud Run env var) into the proxy_pass directive.
COPY nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
