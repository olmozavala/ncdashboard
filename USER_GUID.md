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

## 🏗️ How it Works (High-Level Architecture)

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
