# An enum with the types of plots
import holoviews as hv
import panel as pn
import xarray as xr
import numpy as np

from model.model_utils import PlotType, get_all_coords
from proj_layout.utils import select_colormap

import param
from abc import ABC, ABCMeta, abstractmethod

class ParameterizedABC(param.parameterized.ParameterizedMetaclass, ABCMeta):
    pass

class FigureNode(param.Parameterized, metaclass=ParameterizedABC):
    cmap = param.Parameter()
    cnorm = param.Selector(default='linear', objects=['linear', 'log', 'eq_hist'])
    clim = param.Tuple(default=(None, None), length=2)

    def __init__(self, id, data, title=None, field_name=None, bbox=None, plot_type = PlotType.TwoD, 
                 parent=None,  cmap=None, **params):
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
            '#F2F1EF', # Warm gray (Very pale)
            '#EEF2F5', # Cool gray (Very pale)
            '#F3F7FB', # Very pale blue
            '#F8F6F2', # Very pale beige
            '#E2EAF4', # Muted Blue (Slightly more color)
            '#E2F4EA', # Muted Green (Slightly more color)
            '#F4E2E2', # Muted Pink (Slightly more color)
            '#E5E7EB'  # Muted Slate (Slightly more color)
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
            # If there is a long name, then we use it
            self.long_name = data.long_name.capitalize()
            # If there are units, then we use them
            self.units = data.units
        except:
            pass

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
        '''
        Returns the HoloViews object that should be used as source for streams.
        By default it returns the same as create_figure().
        '''
        return self.create_figure()

    def get_controls(self):
        '''
        Returns a set of controls for the node.
        '''
        return None

    def add_child(self, node):
        self.children.append(node)

    def remove_child(self, node):
        self.children.remove(node)

    # --- All the getters
    def get_animation_coords(self):
        '''
        Returns the coordinates that can be animated
        '''
        animation_coords = []
        if self.plot_type.can_request_animation():
            times, zaxis, _, _= get_all_coords(self.data)
            if times.size > 1:
                animation_coords.append(times.dims[0].capitalize()) # type: ignore
            if zaxis.size > 1:
                animation_coords.append(zaxis.dims[0].capitalize()) # type: ignore

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