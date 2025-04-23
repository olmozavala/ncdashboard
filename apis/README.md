# NC Dashboard API

This repository contains the backend API implementation for the NC Dashboard project. The API is built using FastAPI and follows a clean, modular architecture with clear separation of concerns.

## Repository Structure

```
apis/
├── app.py              # Main application entry point
├── routes/            # API route definitions
│   ├── __init__.py    # Route module initialization
│   ├── cache.py       # Cache-related endpoints
│   ├── data.py        # Data-related endpoints
│   ├── image.py       # Image-related endpoints
│   └── session.py     # Session management endpoints
├── services/          # Business logic and data processing
│   ├── cache.py       # Caching service implementation
│   ├── data.py        # Data processing service
│   ├── db.py          # Database operations
│   └── image.py       # Image processing service
├── models/            # Data models and schemas
├── utils/             # Utility functions and constants
└── requirements.txt   # Python dependencies
```

## Architecture Overview

### 1. Application Entry Point (`app.py`)
- Initializes the FastAPI application
- Configures middleware (CORS, etc.)
- Sets up static file serving
- Implements SPA (Single Page Application) routing
- Manages database lifecycle
- Dynamically loads routes from the routes directory

### 2. Routes Layer (`routes/`)
The routes layer handles HTTP request/response logic and input validation. Each route module:
- Defines API endpoints using FastAPI's router
- Validates incoming requests
- Calls appropriate service layer functions
- Handles error responses
- Returns properly formatted responses

Key route modules:
- `data.py`: Handles dataset-related operations
- `image.py`: Manages image processing endpoints
- `cache.py`: Controls caching operations
- `session.py`: Manages user sessions

### 3. Services Layer (`services/`)
The services layer contains the business logic and data processing. This separation:
- Keeps business logic isolated from HTTP concerns
- Makes the code more testable
- Allows for easier maintenance and updates
- Provides clear separation of responsibilities

Key service modules:
- `db.py`: Database operations and management
- `data.py`: Data processing and transformation
- `cache.py`: Caching implementation (Not currently implemented)
- `image.py`: Image processing logic

### 4. Models Layer (`models/`)
- Defines data structures and schemas
- Contains type definitions
- Implements data validation logic

### 5. Utils Layer (`utils/`)
- Contains shared constants
- Implements utility functions
- Stores configuration values

## Design Patterns and Principles

1. **Separation of Concerns**
   - Routes handle HTTP concerns
   - Services contain business logic
   - Models define data structures
   - Utils provide shared functionality

2. **Dependency Injection**
   - Services are injected into routes
   - Database connections are managed through dependency injection
   - Makes testing and maintenance easier

3. **Error Handling**
   - Centralized error handling through the `ErrorType` enum in `models/errors.py`
   - Consistent error response format across all endpoints
   - Proper HTTP status codes mapping to error types
   - Categorized error types for different domains:
     - General errors (INVALID_REQUEST, INVALID_ROUTE, INTERNAL_ERROR)
     - Dataset errors (INVALID_DATASET, EMPTY_DATASET_DIR, DATASET_NOT_FOUND)
     - Cache errors (CACHE_NOT_FOUND, CACHE_INDEX_ERROR)
     - Image errors (IMAGE_NOT_FOUND)
     - Session errors (SESSION_NOT_FOUND)
   - Error handling flow:
     1. Service layer returns error type values
     2. Route layer converts error types to appropriate HTTP responses
     3. Client receives standardized error responses
   - Benefits:
     - Type-safe error handling
     - Centralized error type management
     - Easy to add new error types
     - Consistent error reporting
     - Improved debugging and maintenance

4. **Configuration Management**
   - Constants stored in utils
   - Environment-specific configuration
   - Easy to modify and maintain

## Data Flow

1. Client request → Route endpoint
2. Route validates input and calls appropriate service
3. Service processes request using business logic
4. Service interacts with database if needed
5. Response flows back through service → route → client

## File Organization

- Each module has a single responsibility
- Related functionality grouped in directories
- Clear naming conventions
- Consistent file structure
- Proper Python package organization with `__init__.py` files

## Best Practices

1. **Code Organization**
   - Modular design
   - Clear file structure
   - Consistent naming conventions

2. **Error Handling**
   - Custom error types
   - Proper exception handling
   - Meaningful error messages

3. **Documentation**
   - Docstrings for functions
   - Type hints
   - Clear comments

4. **Testing**
   - Separated concerns for easier testing
   - Service layer can be tested independently
   - Route layer can be tested with mock services

## Development Workflow

1. Define new endpoints in routes
2. Implement business logic in services
3. Create/update models as needed
4. Add utility functions if required
5. Test and document changes

This architecture ensures:
- Scalability
- Maintainability
- Testability
- Clear separation of concerns
- Easy to understand and modify
