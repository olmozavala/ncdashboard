# NcDashboard User Guide

Welcome to **NcDashboard**, a powerful, interactive tool for visualizing and analyzing oceanographic and atmospheric data stored in NetCDF format. This guide covers the key functionalities available and provides a high-level overview of the dashboard's architecture.

---

## 🚀 Key Functionalities

### 1. Data Exploration & Visualization
- **Multi-File Support**: Load single NetCDF files or entire directories using regular expressions (e.g., `path --regex "*.nc"`).
- **Intelligent Variable Mapping**: The dashboard automatically detects the dimensionality of your data (1D, 2D, 3D, 4D) and organizes variables in the sidebar for easy access.
- **Dynamic Plotting**: One-click plotting for any variable in your dataset.

### 2. Interactive Maps & Plots
- **Multi-Dimensional Navigation**: For 3D (Time or Depth) and 4D (Time and Depth) data, the dashboard provides synchronized sliders to navigate through different layers and time steps.
- **Linked Pan & Zoom**: High-performance maps (powered by Datashader) allow you to explore large datasets smoothly. Zoom level and position are tracked as part of the dashboard state.
- **Automatic Scaling**: Uses robust percentile-based scaling (2% - 98%) to ensure visualizations look good immediately upon loading, even with extreme outliers.

### 3. Drill-Down Analysis (Profiles)
- **Point-and-Click Interaction**: Click any location on a 2D map to instantly generate vertical (depth) or temporal (time-series) profiles for that specific coordinate.
- **Hierarchical Context**: Profile plots are linked to their "parent" map, making it easy to see where data was extracted from.

### 4. Customization & Styling
- **Visual Colormap Gallery**: A built-in gallery allows you to choose from hundreds of scientific colormaps (cmocean, matplotlib, etc.) with real-time previews.
- **Manual Color Limits**: Precisely control the min/max values of your color scale for detailed data comparison.
- **Full-Screen Focus**: Maximize any plot to fill the workspace for closer inspection, and restore it back to the grid when done.

### 5. 🤖 AI-Powered Custom Analysis
- **Natural Language Requests**: Use integrated LLMs (OpenAI, Gemini, etc.) to perform complex analysis by simply asking. For example: *"Calculate the average surface temperature over the first 10 time steps"* or *"Convert sea level anomaly to meters."*
- **Auto-Visualization**: The AI generates the required Python code, executes it on your data, and automatically adds a new interactive plot to your dashboard.

### 6. Session Persistence (Save/Load)
- **Full State Capture**: Save your entire workspace—including active plots, zoom levels, selected time/depth indices, colormaps, and color limits—into a single `.json` file.
- **Quick Restoration**: Reload your state file at any time to resume your analysis exactly where you left off.

---

## Configuration File (`ncdashboard_config.yml`)

NcDashboard is configured through a single YAML file located at the project root: `ncdashboard_config.yml`. The file has two main sections: **LLM** and **Server**.

### LLM Configuration

The `llm` section controls the AI-powered custom analysis feature. You choose a `default_provider` and configure one or more providers under `providers`:

```yaml
llm:
  default_provider: "openai"
  providers:
    openai:
      api_key_env: "OPENAI_API_KEY"
      model: "gpt-4o-mini"

    gemini:
      api_key_env: "GEMINI_API_KEY"
      model: "gemini-2.0-flash"

    anthropic:
      api_key_env: "ANTHROPIC_API_KEY"
      model: "claude-3-5-sonnet-20241022"

    ollama:
      model: "qwen2.5-coder:3b"
      base_url: "http://localhost:11434"
```

| Field | Description |
| :--- | :--- |
| `default_provider` | Which provider to use. Supported values: `openai`, `gemini`, `anthropic`, `ollama`. |
| `api_key_env` | Name of the environment variable holding the API key (e.g. `OPENAI_API_KEY`). Set the variable in your shell before launching the dashboard. |
| `model` | The model identifier to use for that provider. |
| `base_url` | (Ollama only) URL of the local Ollama server. |

For cloud providers, make sure the corresponding environment variable is exported before starting the dashboard:

```bash
export OPENAI_API_KEY="sk-..."
```

For a fully local setup with no API keys, use `ollama` as the default provider and ensure the Ollama server is running.

### Dashboard Title

The `title` field under `server` lets you set a custom title for the dashboard header:

```yaml
server:
  title: "My Ocean Data Explorer"
```

If omitted, the default NcDashboard title is used.

### Remote / Proxied Server Settings

If you plan to deploy NcDashboard on a remote machine (e.g. an HPC cluster) or behind a reverse proxy (e.g. Nginx or Apache), configure the remaining `server` options:

```yaml
server:
  title: "Customized Title"
  host: "0.0.0.0"
  port: 8053
  prefix: "ncdashboard_osc"
  use_xheaders: true
  cdn: true
  autoreload: true
  allow_all_origins: true
  allowed_origins:
    - "yourdomain.edu"
    - "yourdomain.edu:443"
    - "localhost:8053"
```

| Field | Description |
| :--- | :--- |
| `host` | Network interface to bind to. Use `"0.0.0.0"` to accept connections from any address (required for remote access); use `"127.0.0.1"` for local-only. |
| `port` | TCP port the dashboard listens on. Can be overridden from the command line with `--port`. |
| `prefix` | URL path prefix (e.g. `"ncdashboard_osc"` makes the app available at `http://host:port/ncdashboard_osc`). Useful when the dashboard runs behind a reverse proxy alongside other services. |
| `use_xheaders` | Set to `true` when behind a proxy that forwards `X-Forwarded-For` / `X-Forwarded-Proto` headers, so the dashboard sees the real client IP and protocol. |
| `cdn` | When `true`, static JS/CSS assets are loaded from a public CDN instead of the local server. Reduces bandwidth on the host and can improve load times for remote users. |
| `autoreload` | Automatically restarts the server when source files change. Useful during development but should be set to `false` in production, as it can cause figure drops on active connections. |
| `allow_all_origins` | When `true`, accepts WebSocket connections from any origin. Convenient for development or when users access the dashboard through varying hostnames. |
| `allowed_origins` | An explicit list of allowed WebSocket origins (hostnames with optional ports). These are always allowed in addition to `localhost` and the configured `host:port`. |

---

## How it Works (High-Level Architecture)

NcDashboard is built on a modern Python stack (**Panel**, **HoloViews**, **Xarray**) and follows a decoupled **Model-View-Controller (MVC)** design pattern.

### 1. The Model (Figure Tree)
The core of the dashboard is represented as a **tree of FigureNodes**.
- Every visual element on your screen is a "node".
- Root-level nodes usually represent variables from the NetCDF file.
- Child nodes (like profiles or animations) "inherit" data and context from their parents.
- This structure allows the dashboard to manage complex dependencies and maintain state across different types of visualizations.

### 2. Data Handling (Xarray)
Data is managed using **Xarray**, which provides a powerful N-dimensional array interface.
- **Lazy Loading**: Data is only loaded from disk when needed for a plot, allowing the dashboard to handle datasets much larger than your available RAM.
- **Coordinate-Aware**: Operations (like clicks or slicing) are performed using physical coordinates (lat, lon, time, depth) rather than simple array indices.

### 3. Visualization Engine (HoloViz)
The dashboard leverages the **HoloViz ecosystem**:
- **HoloViews/GeoViews**: Defines *what* to plot. This allows the dashboard to stay backend-independent (switching between Bokeh for interactivity and Datashader for big data).
- **Panel**: Acts as the controller and layout engine. It manages the sidebar, header, and the dynamic grid of figures, handling all the asynchronous callbacks and event linking.

### 4. State Management
When you click "Save State", NcDashboard performs a **recursive serialization** of the FigureNode tree. It walks down the tree, capturing the configuration of every node. During "Load State", it rebuilds the tree from the JSON definition and re-links interactive features (like map-click listeners) to the new UI components.
