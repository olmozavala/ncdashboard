# ncdashboard
An Open Source project to generate dynamic visualizations of ocean and atmospheric data. 

## Installation

Ensure you have access to the pre-configured `uv` environment.

1. Use the python executable from the `uv` environment to run the dashboard:
    ```bash
    /home/olmozavala/uv/envs/eoasweb/bin/python ncdashboard_panel.py path_to_file
    ```

## Running
To run the dashboard, provide the path to the NetCDF file or files you wish to visualize:

```bash
python ncdashboard_panel.py test.nc
```

If you have multiple files, use regular expressions to select them:

```bash
python ncdashboard_panel.py path --regex "*.nc"
```

You can also specify a port (overrides the config file):

```bash
python ncdashboard_panel.py path --regex "*.nc" --port 8053
```

## Configuration

The dashboard is configured via the `ncdashboard_config.yml` file located in the project root. This file controls server settings, the header title, reverse proxy support, and LLM integration.

### Example Configuration

```yaml
# NcDashboard Configuration File

# --- Dashboard Server Settings ---
server:
  title: "HYCOM GOMb0.04 Reanalysis"
  host: "0.0.0.0"
  port: 8053
  prefix: "ncdashboard_osc"
  use_xheaders: true
  cdn: true
  allow_all_origins: true
  allowed_origins:
    - "example.com"
    - "localhost:8053"

# --- LLM Configuration ---
llm:
  default_provider: "openai"
  providers:
    openai:
      api_key_env: "OPENAI_API_KEY"
      model: "gpt-4o-mini"
```

### Server Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `title` | string | *(none)* | Custom title displayed in the header after "NcDashboard". Example: `"HYCOM GOMb0.04 Reanalysis"` produces **NcDashboard — HYCOM GOMb0.04 Reanalysis**. |
| `host` | string | `"127.0.0.1"` | Network interface to bind to. Use `"0.0.0.0"` to accept connections from any interface (required for remote access). |
| `port` | integer | `8050` | Port number for the server. Can be overridden with `--port` on the command line. |
| `prefix` | string | *(none)* | URL prefix for serving behind a reverse proxy. For example, `"ncdashboard_osc"` serves the app at `http://host:port/ncdashboard_osc`. |
| `use_xheaders` | boolean | `false` | Enable when running behind a reverse proxy (e.g., Apache, Nginx) so the app correctly reads forwarded headers. |
| `cdn` | boolean | `false` | Serve Bokeh/Panel static resources from CDN instead of locally. Recommended when behind a reverse proxy to avoid 404 errors on static files. |
| `allow_all_origins` | boolean | `false` | Allow WebSocket connections from any origin. Useful for debugging but less secure for production. |
| `allowed_origins` | list of strings | `[]` | Explicit list of allowed WebSocket origins. Always include the public domain and any local addresses used for access. |

### LLM Settings

| Setting | Type | Description |
|---------|------|-------------|
| `default_provider` | string | The LLM provider to use (e.g., `"openai"`). |
| `providers.<name>.api_key_env` | string | Name of the environment variable containing the API key. |
| `providers.<name>.model` | string | Model identifier to use (e.g., `"gpt-4o-mini"`). |

### Reverse Proxy Setup (Apache)

When deploying behind Apache, you need to enable WebSocket proxying. Add the following to your Apache configuration:

```apache
# NcDashboard
ProxyPass /ncdashboard_osc/ http://localhost:8053/ncdashboard_osc/
ProxyPassReverse /ncdashboard_osc/ http://localhost:8053/ncdashboard_osc/

# WebSocket support
RewriteEngine On
RewriteCond %{HTTP:Upgrade} websocket [NC]
RewriteCond %{HTTP:Connection} upgrade [NC]
RewriteRule ^/ncdashboard_osc/(.*) ws://localhost:8053/ncdashboard_osc/$1 [P,L]
```

## Examples
This section contains examples of the visualizations generated using example data in the `test_data` directory.

### Single NetCDF file

```bash
python ncdashboard_panel.py test_data/gom_t007.nc
```

### Multiple NetCDF files with regex

```bash
python ncdashboard_panel.py test_data --regex "*.nc"
```

![Alt Text](figs/example.gif)

## Links

- [GitHub Repository](https://github.com/olmozavala/ncdashboard)
- [Panel Documentation](https://panel.holoviz.org/)
- [HoloViews Documentation](https://holoviews.org/)
- [GeoViews Documentation](https://geoviews.org/)