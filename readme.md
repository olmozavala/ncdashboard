# NC Dashboard

A modern web application built with React, TypeScript, and FastAPI for data visualization and analysis.

## Project Structure

This project follows a monorepo structure with the following components:

- `web/` - Frontend React application with TypeScript
- `apis/` - Backend FastAPI server
- `test_data/` - Directory for test data files
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - Multi-stage build for the application
- `ngrok.yml` - Configuration for secure tunneling

## Technology Stack

### Frontend
- React with TypeScript
- Vite for build tooling
- Modern UI components

### Backend
- FastAPI (Python web framework)
- Xarray for data manipulation
- Uvicorn as the ASGI server

## Development Setup

### Prerequisites
- Node.js 22 LTS
- Python 3.12
- Docker and Docker Compose
- Optional: Ngrok account (Only needed if working with deployment)

### Environment Configuration

1. Create a `.env` file in the `web` directory with:
```env
VITE_BACKEND_API_URL=http://localhost:8000
```

### Local Development

You can run the application in development mode using two separate terminals:

1. Start the API server:
```sh
cd apis && bash api.sh --dev
```

2. Start the frontend development server:
```sh
cd web && bash web.sh --dev
```

## Docker Deployment

The application can be deployed using Docker Compose, which sets up:
- The ncdashboard service 
- An Ngrok tunnel for secure public access

Before deploying, create an `ngrok.yml` file in the root directory with the following structure (note: this file is not included in the repository as it contains sensitive API keys):
```yaml
version: 3
agent:
  authtoken: YOUR_NGROK_AUTH_TOKEN
endpoints:
  - name: flowise
    url: YOUR_NGROK_URL
    upstream:
      url: http://ncdashboard:3030
```

Replace `YOUR_NGROK_AUTH_TOKEN` with your actual Ngrok authentication token and `YOUR_NGROK_URL` with your desired Ngrok URL.

To build and run with Docker:

```sh
# Build the containers
COMMIT_HASH=$(git rev-parse --short HEAD) docker compose build

# Start the services
docker compose up
```

The application will be available at:
- Local: http://localhost:3030
- Public: Accesible at `YOUR_NGROK_URL` Via Ngrok tunnel

## Build Process

The application uses a multi-stage Dockerfile that:
1. Builds the React frontend using Node.js
2. Creates a Python container with the FastAPI
3. Combines both into a single production-ready image

## Security Notes

- The Ngrok tunnel provides secure public access to the application
- API keys and sensitive data should be managed through environment variables
- The application runs in isolated Docker networks for security

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
