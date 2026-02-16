# An enum with the types of plots
import holoviews as hv
import geoviews as gv
import cartopy.crs as ccrs
import panel as pn
import xarray as xr
import numpy as np

from model.model_utils import PlotType, get_all_coords
from proj_layout.utils import select_colormap

import param
from abc import ABC, ABCMeta, abstractmethod
from loguru import logger

class ParameterizedABC(param.parameterized.ParameterizedMetaclass, ABCMeta):
    pass

class FigureNode(param.Parameterized, metaclass=ParameterizedABC):
    cmap = param.Parameter()
    cnorm = param.Selector(default='linear', objects=['linear', 'log', 'eq_hist'])
    clim = param.Tuple(default=(None, None), length=2)

    # Default tools and active tools for all geo plots
    GEO_TOOLS = ['pan', 'wheel_zoom', 'save', 'copy', 'reset', 'hover']
    GEO_ACTIVE_TOOLS = ['pan']

    def __init__(self, id, data, title=None, field_name=None, bbox=None, plot_type=PlotType.TwoD, 
                 parent=None, cmap=None, **params):
        super().__init__(**params)
        self.parent = parent
        self.id = id
        self.bbox = bbox
        self.children = []
        self.field_name = field_name
        self.view_container = None
        self.add_node_callback = None
        self.id_generator_callback = None
        self.maximized = False
        self.cnorm = 'linear'
        
        # Background color for relationship tracking
        PASTEL_COLORS = [
            '#F2F1EF', '#EEF2F5', '#F3F7FB', '#F8F6F2',
            '#E2EAF4', '#E2F4EA', '#F4E2E2', '#E5E7EB'
        ]
        
        if 'background_color' in params:
            self.background_color = params['background_color']
        elif parent and hasattr(parent, 'background_color') and parent.id != 'root':
            self.background_color = parent.background_color
        else:
            import random
            self.background_color = random.choice(PASTEL_COLORS)
        
        # Stream for click marker
        self.marker_stream = hv.streams.Tap(x=None, y=None)
        self.clicked_points = []



        self.long_name = field_name
        self.units = 'no units'
        self.data = data
        try:
            self.long_name = data.long_name.capitalize()
            self.units = data.units
        except:
            pass

        self.label = f"{self.long_name} ({self.units})"

        if title is None:
            self.title = self.long_name
        else:
            self.title = title

        self.coord_names = np.array(list(data.dims)) 
        self.plot_type = plot_type

        if cmap is None:
            if field_name is not None:
                self.cmap = select_colormap(self.field_name)
        else:
            self.cmap = cmap

    # -------- Shared Geo-Plotting Helpers ---------

    @staticmethod
    def _activate_wheel_zoom(plot, element):
        """Bokeh hook to force wheel_zoom as the active scroll tool.
        HoloViews' active_tools only handles drag/tap tools, not scroll."""
        from bokeh.models import WheelZoomTool
        for tool in plot.state.toolbar.tools:
            if isinstance(tool, WheelZoomTool):
                plot.state.toolbar.active_scroll = tool
                break

    def _build_marker_overlay(self):
        """Create the click-marker DynamicMap overlay (yellow=previous, red=latest)."""
        def _get_marker(x, y):
            kdims = [self.coord_names[-1], self.coord_names[-2]]
            prev_points = self.clicked_points[:-1]
            latest_point = self.clicked_points[-1:]
            p_prev = gv.Points(prev_points, kdims=kdims, crs=ccrs.PlateCarree()).opts(
                color='yellow', size=12, marker='star', line_color='black', line_width=1
            )
            p_latest = gv.Points(latest_point, kdims=kdims, crs=ccrs.PlateCarree()).opts(
                color='red', size=15, marker='star', line_color='black', line_width=1
            )
            return p_prev * p_latest
        return gv.project(
            hv.DynamicMap(_get_marker, streams=[self.marker_stream]),
            projection=ccrs.GOOGLE_MERCATOR
        )

    def _build_geo_overlay(self, rasterized, **extra_opts):
        """Assemble the final geo overlay: tiles * rasterized * markers,
        with standard tools and the wheel_zoom hook applied."""
        tiles = gv.tile_sources.OSM()
        base = (tiles * rasterized).opts(
            tools=self.GEO_TOOLS,
            active_tools=self.GEO_ACTIVE_TOOLS,
            **extra_opts
        )
        marker_dmap = self._build_marker_overlay()
        return (base * marker_dmap).opts(hooks=[self._activate_wheel_zoom])



    # -------- Tree Methods ---------

    def locate(self, id) -> 'FigureNode':
        '''Returns the node with the given id'''
        if self.id == id:
            return self
        else:
            for child in self.children:
                found = child.locate(id)
                if found is not None:
                    return found
        return None # type: ignore

    def remove_id(self, id):
        '''Removes the node with the given id'''
        if self.id == id:
            if self.parent.children is None:
                print("Error: parent children is None, I'm the root")
            else:
                self.parent.children.remove(self)
        else:
            for child in self.children:
                child.remove_id(id)

    # -------- Plotting methods ---------
    @abstractmethod
    def create_figure(self):
        pass

    def get_stream_source(self):
        '''Returns the HoloViews object that should be used as source for streams.
        For geo nodes with a dmap, returns self.dmap. Otherwise falls back to create_figure().'''
        if hasattr(self, 'dmap'):
            return self.dmap
        return self.create_figure()

    def get_controls(self):
        '''Returns a set of controls for the node.'''
        return None

    def add_child(self, node):
        self.children.append(node)

    def remove_child(self, node):
        self.children.remove(node)

    # --- All the getters
    def get_animation_coords(self):
        '''Returns the coordinates that can be animated'''
        animation_coords = []
        if self.plot_type.can_request_animation():
            times, zaxis, _, _ = get_all_coords(self.data)
            if times.size > 1:
                animation_coords.append(times.dims[0].capitalize())
            if zaxis.size > 1:
                animation_coords.append(zaxis.dims[0].capitalize())
        return animation_coords

    def get_data(self) -> xr.DataArray:
        return self.data

    def get_parent(self):
        return self.parent

    def get_coord_names(self):
        return list(self.data.dims)

    def get_field_name(self):
        return self.field_name

    def get_long_name(self):
        return self.long_name

    def get_bbox(self):
        return self.bbox
    
    def get_cmap(self):
        return self.cmap

    def get_children(self):
        return self.children
    
    def get_id(self):
        return self.id

    def get_plot_type(self):
        return self.plot_type
    
    # --- All the setters
    def set_data(self, data):
        self.data = data

    def set_parent(self, parent):
        self.parent = parent

    def set_bbox(self, bbox):
        self.bbox = bbox
    
    def set_cmap(self, cmap):
        self.cmap = cmap
    
    def set_id(self, id):
        self.id = id

    def set_field_name(self, field_name):
        self.field_name = field_name

    def set_plot_type(self, plot_type):
        self.plot_type = plot_type

    def __str__(self):
        return f'ID: {self.id} BBOX: {self.bbox}'