###############################################################################
# Multi‑stage Dockerfile                                                       #
#                                                                             #
# ──────────────── How to build with your Git commit hash ─────────────────── #
# • Plain Docker:                                                              #
#     COMMIT=$(git rev-parse --short HEAD)                                    #
#     docker build --build-arg COMMIT_HASH=$COMMIT -t myapp:$COMMIT .          #
#                                                                             #
# • Docker Compose (service “backend”):                                        #
#     COMMIT_HASH=$(git rev-parse --short HEAD) docker compose build backend   #
#                                                                             #
# The build arg is passed to Vite as VITE_COMMIT_HASH, letting your SPA        #
# display or log the exact source revision of the image.                       #
#                                                                             #
# ──────────────────────────────────────────────────────────────────────────── #
# Stage 1: Build the React/Vite front‑end                                     #
# Stage 2: Build the FastAPI back‑end and serve the compiled static assets    #
#                                                                             #
# The final image contains only:                                              #
#   • a slim Python runtime                                                   #
#   • the back‑end application code                                           #
#   • the pre‑compiled front‑end bundle                                       #
###############################################################################

###############################
# Stage 1 – Front‑end builder #
###############################

# Build‑time argument (override with --build-arg COMMIT_HASH=<sha>)
ARG COMMIT_HASH=dev

# Use the official Node.js 22 LTS image to compile the SPA
FROM node:22 AS frontend-builder

# Root directory for build operations
WORKDIR /app

# Provide build‑time metadata to Vite
ENV VITE_COMMIT_HASH=$COMMIT_HASH
ENV VITE_BACKEND_API_URL=https://pheasant-up-overly.ngrok-free.app/api

# Copy only the front‑end source tree to keep the context lean
COPY web ./web

# Install dependencies (lockfile ensures reproducibility) and build
WORKDIR /app/web
RUN yarn install --frozen-lockfile
RUN yarn build          # Output bundled assets to /app/web/dist



########################################
# Stage 2 – Back‑end and static assets #
########################################

# Start from a minimal Python 3.12 base image
FROM python:3.12-slim

# Application root in the final image
WORKDIR /app

# ---------------------------------------------------------------------------
# Install Python dependencies for the FastAPI back‑end
# ---------------------------------------------------------------------------
COPY apis ./apis
WORKDIR /app/apis
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Copy the compiled front‑end bundle from Stage 1
# Placed at /app/web/dist alongside the back‑end
# ---------------------------------------------------------------------------
COPY --from=frontend-builder /app/web/dist ../web/dist

# ---------------------------------------------------------------------------
# Launch the FastAPI app with Uvicorn
#   --host 0.0.0.0   Listen on all interfaces
#   --port 3030      Container port (map with -p 3030:3030)
# ---------------------------------------------------------------------------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3030"]
