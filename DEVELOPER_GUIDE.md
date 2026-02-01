# NcDashboard Developer Guide

This document provides a technical overview of the NcDashboard architecture, designed to help developers (and AI agents) understand how the components interact.

## 1. Architecture Overview (MVC)

NcDashboard follows a decoupled Model-View-Controller pattern:

- **Model**: Located in `model/`. Orchestrates data loading (via `xarray`) and manages the hierarchical representation of figures (`FigureNode` tree).
- **View/Controller**:
  - **Panel**: `ncdashboard_panel.py` (Primary)
  - **Dash**: `controller.py` (Secondary/Experimental)

## 2. The Figure Tree (`FigureNode`)

The dashboard state is managed by a tree of `FigureNode` objects.

### Core Hierarchy
- `FigureNode` (Base Class in `model/FigureNode.py`)
  - `TwoDNode`: 2D Map plots (lat/lon).
  - `ThreeDNode`: 3D plots (Adds a third dimension like Time or Depth with navigation).
    - `FourDNode`: 4D plots (Handles both Time and Depth).
  - `AnimationNode`: Specialized node for animated plots.
  - `ProfileNode`: 1D plots (e.g., vertical profiles from a map click).

### Key Attributes
- `id`: Unique identifier (e.g., `water_temp_1`).
- `parent`: Reference to the parent node (`root` is a special ID).
- `children`: List of child nodes.
- `background_color`: Assigned to root-level nodes and inherited by children for visual grouping.
- `maximized`: Boolean flag for "full screen" state.

## 3. Data Flow and Figure Creation

1. **Selection**: User selects variables in the sidebar.
2. **Creation**: `Dashboard.create_default_figure` is called.
3. **Instantiation**: The appropriate `FigureNode` subclass is instantiated.
4. **UI Wrapping**: The `Dashboard` wraps the node's HoloViews/Plotly object into a UI container (Panel `Column` or Dash `html.Div`).
5. **Event Linking**:
   - `marker_stream` (hv.streams.Tap): Handles map clicks to trigger `create_profiles`.
   - `range_stream` (hv.streams.RangeXY): Tracks viewport (zoom/pan) for state persistence.

## 4. Save/Load State Implementation

State logic is encapsulated in `model/state.py` and `model/dashboard.py`.

### Serialization (`model/state.py`)
- `get_state_from_dashboard`: Walks the `FigureNode` tree (depth-first).
- `_serialize_node`: Converts a node into a dictionary.
- **Includes**: Colormaps, normalization (`cnorm`), coordinates (`time_idx`, `depth_idx`), viewport ranges (`x_range`, `y_range`), and visual flags (`maximized`, `background_color`).

### Restoration (`model/dashboard.py`)
- `apply_state`:
  1. Sorts serialized figures by parent-child depth.
  2. Recreates root nodes first.
  3. Recreates child nodes (profiles, animations) using `_restore_figure`.
  4. Re-links viewport streams to the new UI containers.

## 5. UI Organization (Panel)

- **Sidebar**: Defined in `ncdashboard_panel.py:init_menu`. Action buttons (Close All, Save/Load) are at the top, followed by variable-specific buttons for one-click plotting.
- **Main Area**: Static `FlexBox` or `Column` where figure containers are appended.

## 6. Common Development Tasks

### Adding a new Plot Type
1. Create a new subclass of `FigureNode` in `model/`.
2. Implement `create_figure()`.
3. Update `Dashboard.create_default_figure` to instantiate your new class.
4. Update `_serialize_node` in `state.py` if the new node has unique attributes.

### Handling Coordinate Ordering
- Most nodes assume the last two dimensions are spatial (Lat/Lon).
- 3D/4D nodes expect Z/T dimensions at specific indices. See `model_utils.py` for selection helpers.

## 7. Known Quirks
- **Resolutions Enum**: Values are currently swapped (`HIGH="low"`, `LOW="high"`) in `model_utils.py` due to internal logic dependencies; do not "fix" without refactoring `AnimationNode`.
- **Viewport Streams**: Range streams must be linked *after* the figure is wrapped in a Panel/Dash component for correct synchronization.
