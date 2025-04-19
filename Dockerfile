# --- Stage 1: Build frontend ---
ARG COMMIT_HASH=dev
FROM node:22 AS frontend-builder

WORKDIR /app
ENV VITE_COMMIT_HASH=$COMMIT_HASH
ENV VITE_BACKEND_API_URL=https://pheasant-up-overly.ngrok-free.app/api
COPY web ./web
WORKDIR /app/web
RUN yarn install
RUN yarn build

# --- Stage 2: Build backend and serve frontend ---
FROM python:3.12-slim

WORKDIR /app

# Install backend requirements

COPY apis ./apis
WORKDIR /app/apis
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/web/dist ../web/dist

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3030"]
