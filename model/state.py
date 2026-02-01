"""
Serialize and restore dashboard state (figures tree, colormaps, zoom, etc.)
for save/load configuration as JSON or YAML.
"""
from __future__ import annotations

import json
from typing import Any

from model.FigureNode import FigureNode
from model.model_utils import PlotType


def _cmap_to_name(cmap: Any) -> str:
    """Return a string name for a colormap (matplotlib or string)."""
    if cmap is None:
        return "viridis"
    if isinstance(cmap, str):
        return cmap
    if hasattr(cmap, "name"):
        return getattr(cmap, "name", "").split(".")[-1] or "viridis"
    return "viridis"


def _serialize_node(node: FigureNode, parent_id: str) -> dict[str, Any]:
    """
    Build a serializable state dict for one figure node.
    parent_id is the id of the parent node ('root' for top-level).
    """
    plot_type = node.get_plot_type()
    pt_name = plot_type.name if isinstance(plot_type, PlotType) else str(plot_type)

    state: dict[str, Any] = {
        "id": node.get_id(),
        "plot_type": pt_name,
        "field_name": node.get_field_name(),
        "parent_id": parent_id,
        "cmap": _cmap_to_name(node.get_cmap()),
        "cnorm": getattr(node, "cnorm", "linear"),
    }

    # View extent (zoom/domain) for 3D/4D nodes that have range_stream
    if hasattr(node, "range_stream") and node.range_stream is not None:
        xr = getattr(node.range_stream, "x_range", None)
        yr = getattr(node.range_stream, "y_range", None)
        if xr is not None and yr is not None:
            try:
                state["x_range"] = list(xr) if hasattr(xr, "__iter__") else [xr, xr]
                state["y_range"] = list(yr) if hasattr(yr, "__iter__") else [yr, yr]
            except (TypeError, ValueError):
                pass

    # 3D / 4D slice indices
    if hasattr(node, "third_coord_idx"):
        state["third_coord_idx"] = node.third_coord_idx
    if hasattr(node, "time_idx"):
        state["time_idx"] = node.time_idx
    if hasattr(node, "depth_idx"):
        state["depth_idx"] = node.depth_idx

    # Animation nodes: coord, resolution, current frame
    if hasattr(node, "animation_coord"):
        state["animation_coord"] = node.animation_coord
    if hasattr(node, "spatial_res"):
        state["spatial_res"] = node.spatial_res
    if hasattr(node, "player"):
        state["frame_idx"] = node.player.value

    # Profile nodes: location and dimension
    if hasattr(node, "lat") and hasattr(node, "lon") and hasattr(node, "dim_prof"):
        state["lat"] = float(node.lat)
        state["lon"] = float(node.lon)
        state["dim_prof"] = node.dim_prof

    state["background_color"] = getattr(node, "background_color", None)
    state["maximized"] = getattr(node, "maximized", False)

    return state


def _collect_figures_depth_first(node: FigureNode, parent_id: str) -> list[dict[str, Any]]:
    """Walk tree depth-first and collect state for each node (excluding root)."""
    out: list[dict[str, Any]] = []
    out.append(_serialize_node(node, parent_id))
    for child in node.get_children():
        out.extend(_collect_figures_depth_first(child, node.get_id()))
    return out


def get_state_from_dashboard(dashboard: Any) -> dict[str, Any]:
    """
    Build full dashboard state (path, regex, figures tree) for saving.

    Args:
        dashboard: Dashboard instance with tree_root, path, regex.

    Returns:
        Dict with keys: version, path, regex, figures (list of node states).
    """
    figures: list[dict[str, Any]] = []
    for child in dashboard.tree_root.get_children():
        figures.extend(_collect_figures_depth_first(child, "root"))

    path = getattr(dashboard, "path", "")
    if isinstance(path, list):
        path = path[0] if path else ""
    regex = getattr(dashboard, "regex", "")

    return {
        "version": 1,
        "path": path,
        "regex": regex,
        "figures": figures,
    }


def save_state_json(dashboard: Any) -> str:
    """Return dashboard state as JSON string (for file download)."""
    return json.dumps(get_state_from_dashboard(dashboard), indent=2)


def load_state_file(path: str) -> dict[str, Any]:
    """
    Load state from a JSON or YAML file.

    Args:
        path: Path to state file (.json or .yml/.yaml).

    Returns:
        State dict with version, path, regex, figures.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    if path.lower().endswith(".json"):
        return json.loads(raw)
    try:
        import yaml
        return yaml.safe_load(raw)
    except ImportError:
        raise ValueError("YAML file given but PyYAML not installed; use .json or install pyyaml") from None
