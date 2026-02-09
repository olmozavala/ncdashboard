import cmocean
import colorcet as cc
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from functools import lru_cache

# Comprehensive list of colormaps grouped by source/type
CMAP_GROUPS = {
    "Cmocean": ['thermal', 'haline', 'algae', 'matter', 'turbid', 'speed', 'amp', 'tempo', 'gray', 'balance', 'curl', 'diff', 'oxy', 'dense', 'ice', 'deep'],
    "Colorcet": ['rainbow', 'fire', 'bgy', 'bgyw', 'bky', 'kbc', 'coolwarm', 'CET_L1', 'CET_L2', 'CET_R2', 'CET_D1', 'phase', 'cyclic_rainbow'],
    "Standard": ['viridis', 'inferno', 'plasma', 'magma', 'cividis', 'rainbow', 'jet', 'nipy_spectral', 'gist_rainbow', 'terrain', 'ocean', 'RdBu_r', 'Spectral_r', 'twilight']
}

CNORM_OPTIONS = ['linear', 'log', 'eq_hist']

def get_available_cmaps():
    """Returns a flat list of all available colormap names."""
    all_cmaps = []
    for group in CMAP_GROUPS.values():
        all_cmaps.extend(group)
    # Remove duplicates but preserve order
    return list(dict.fromkeys(all_cmaps))

@lru_cache(maxsize=128)
def get_cmap_css_gradient(name, steps=10):
    """
    Returns a CSS linear-gradient string for the given colormap name.
    """
    cmap_obj = get_cmap_object(name)
    try:
        # Resolve to a matplotlib colormap if possible
        if isinstance(cmap_obj, str):
            cmap = plt.get_cmap(cmap_obj)
        else:
            cmap = cmap_obj
            
        # If the cmap is a list (e.g. from Colorcet), wrap it in a ListedColormap
        if not callable(cmap):
            cmap = mcolors.ListedColormap(cmap)

        # Sample the colormap
        colors = [cmap(i) for i in np.linspace(0, 1, steps)]
        # Convert to hex
        hex_colors = [mcolors.to_hex(c) for c in colors]
        return f"linear-gradient(to right, {', '.join( hex_colors)})"
    except Exception as e:
        # print(f"Error generating CSS gradient for {name}: {e}")
        return "linear-gradient(to right, gray, white)"

def get_cmap_html_preview(name, width='100%', height='20px'):
    """
    Returns an HTML div with a background gradient representing the colormap.
    """
    gradient = get_cmap_css_gradient(name)
    return f'<div style="width: {width}; height: {height}; background: {gradient}; border-radius: 4px; border: 1px solid #ccc;"></div>'

def get_cmap_object(name):
    """Resolve colormap name to a colormap object (cmocean, colorcet, or string)."""
    if not isinstance(name, str):
        return name

    # Try Cmocean first
    if name in CMAP_GROUPS["Cmocean"]:
        if hasattr(cmocean.cm, name):
            return getattr(cmocean.cm, name)
    
    # Try Colorcet
    if name in CMAP_GROUPS["Colorcet"] or name.startswith('CET_'):
        if hasattr(cc, name):
            return getattr(cc, name)
            
    return name

def select_colormap(field_name):
    '''
    Based on the name if the field it chooses a colormap from cmocean.
    Returns the colormap object directly, compatible with HoloViews/Matplotlib.
    '''
    field_name = field_name.lower()
    cmap = cmocean.cm.thermal # Sensible default
    if np.any([field_name.find(x) != -1 for x in ('ssh', 'srfhgt', 'adt','surf_el')]):
        cmap = cmocean.cm.curl
    elif np.any([field_name.find(x) != -1 for x in ('temp', 'sst', 'temperature','t2m')]):
        cmap = cmocean.cm.thermal
    elif np.any([field_name.find(x) != -1 for x in ('vorticity', 'vort')]):
        cmap = cmocean.cm.curl
    elif np.any([field_name.find(x) != -1 for x in ('salin', 'sss', 'sal')]):
        cmap = cmocean.cm.haline
    elif np.any([field_name.find(x) != -1 for x in ('chlor-a', 'chlora', 'dchl', 'nchl')]):
        cmap = cmocean.cm.algae
    elif field_name.find('error') != -1:
        cmap = cmocean.cm.diff
    elif field_name.find('binary') != -1:
        cmap = cmocean.cm.oxy
    elif np.any([field_name.find(x) != -1 for x in ('u10', 'v10', 'u_', 'v_', 'u-vel.', 'v-vel.','velocity')]):
        cmap = cmocean.cm.speed
    else:
        # If nothing matches, use colorcet rainbow or viridis
        cmap = 'viridis'

    return cmap