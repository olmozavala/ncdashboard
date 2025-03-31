Going with a monorepo structure.  
---
For frontend -
    React with typescript

For backend - 
    FastAPI 
    Xarray

To start the project in dev mode, you will need an `.env` file placed inside the web folder.
This .env file should contain:
```
VITE_BACKEND_API_URL=http://localhost:8000
```

Then, you can start the project in dev mode by running the following commands in two separate terminals.
1. Start the api server.
```sh
cd apis && bash api.sh --dev
```

2. Start the Client.
```sh
cd web && bash web.sh --dev
```


