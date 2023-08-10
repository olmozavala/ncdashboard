# An enum with the types of plots
from enum import Enum
from model.model_utils import PlotType, get_all_coords, select_anim_data
import plotly.graph_objects as go
from dash import dcc
import xarray as xr
import numpy as np

from proj_layout.utils import get_buttons_config, get_def_slider, get_update_buttons, select_colormap

class TreeNode:
    def __init__(self, id, data, title=None, field_name=None, bbox=None, spatial_res=None, 
                 plot_type = PlotType.TwoD, parent=None,  cmap=None, animation=False, 
                 anim_coord_name=None):
        self.parent = parent
        self.id = id
        self.bbox = bbox
        self.spatial_res = spatial_res
        self.children = []
        self.field_name = field_name

        self.long_name = field_name
        self.units = 'no units'
        try:
            # If there is a long name, then we use it
            self.long_name = data.long_name
        except:
            pass

        try:
            # If there are units, then we use them
            self.units = data.units
        except:
            pass

        if title is None:
            self.title = id
        else:
            self.title = title

        self.coord_names = np.array(list(data.coords.keys())) # type: ignore

        # TODO Move outside of constructor
        if spatial_res is None:
            self.data = data
        else:
            coarsen = 1
            if spatial_res == 'medium':
                coarsen = 4
            if spatial_res == 'low':
                coarsen = 8
            self.data = data.coarsen({self.coord_names[-2]:coarsen, 
                                      self.coord_names[-1]:coarsen}, boundary='trim').mean()

        self.plot_type = plot_type

        # ----------- Only used if it is an animation (TODO move to another class)
        self.animation = animation
        self.anim_coord_name = ''

        if cmap is None:
            if field_name is not None:
                self.cmap = select_colormap(self.field_name)

        if animation:
            self.anim_coord_name = anim_coord_name

    def locate(self, id) -> 'TreeNode':
        '''Returns the node with the given id'''
        if self.id == id:
            return self
        else:
            for child in self.children:
                found = child.locate(id)
                if found is not None:
                    return found
        return None

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

    def create_figure(self):
        if self.plot_type == PlotType.OneD:
            return self._create_1d_figure()
        if self.plot_type == PlotType.ThreeD or self.plot_type == PlotType.FourD:
            return self._create_3d4d_figure()
        if self.plot_type == PlotType.ThreeD_Animation or self.plot_type == PlotType.FourD_Animation:
            return self._create_3d4danimation_figure()

    def _create_1d_figure(self):
        
        dims = self.data.dims  # Get the list of dimensions

        # Let's fix the first N-1 dimensions at their 0th index (can be changed as needed)
        indexing_dict = {dim: 0 for dim in dims[:-1]}  # Assuming always the last dimension is the one to be plotted
        coordinate = self.data.coords[dims[-1]]

        # Now, you can index your array using this dictionary
        # This will give you a 1D array along the last dimension
        profile = self.data.isel(indexing_dict)

        # Get the non nan indexes from the profile and clip the coordinate
        non_nan_indexes = np.where(~np.isnan(profile))[0]
        profile = profile[non_nan_indexes]
        coordinate = coordinate[non_nan_indexes]

        # Get the units of the coordinate
        try:
            units_y = coordinate.units
        except:
            units_y = 'no units'


        # Hack to flip the y axis if the dimension is depth and it is positive
        if dims[-1] == 'depth' and coordinate.values[1] > coordinate.values[0]:
            coordinate = -coordinate

        new_graph = dcc.Graph(
                id={"type": "figure_1d", "index": self.id},
                figure=go.Figure(
                        data=[go.Scatter(x=profile, y=coordinate.values, mode='lines+markers')], 
                        layout=go.Layout(
                                title=self.title, 
                                title_x=0.5,
                                height=350,
                                margin=dict(
                                    l=0,  # left margin
                                    r=0,  # right margin
                                    b=0,  # bottom margin
                                    t=30,  # top margin
                                    pad=0  # padding
                                ),
                                yaxis_title=f'{dims[-1].capitalize()} ({units_y})',
                                xaxis_title=f'{self.long_name} ({self.units})',
                            ),
                    ),
            config=get_buttons_config(),
        )
        return new_graph

    def _create_3d4d_figure(self):
        colormap = self.cmap
        data = self.data  # Because it is 3D we assume the spatial coordinates are the last 2
        times, _, lats, lons = get_all_coords(data)
        lats = lats.values
        lons = lons.values

        if self.plot_type == PlotType.ThreeD:
            data = data[0,:,:]
        if self.plot_type == PlotType.FourD:
            data = data[0, 0,:,:]

        new_graph = dcc.Graph(
                id={"type": "figure", "index": self.id},
                figure=go.Figure(
                        data=[go.Heatmap(z=data, colorscale=colormap, showscale=True, x=lons, y=lats)], 
                        layout=go.Layout(title=self.id, 
# zoom, pan, select, lasso, orbit, turntable, zoomInGeo, zoomOutGeo, autoScale2d, resetScale2d, hoverClosestCartesian, hoverClosestGeo, hoverClosestGl2d, hoverClosestPie, toggleHover, resetViews, toggleSpikelines, resetViewMapbox
                                dragmode="pan", 
                                height=350,
                                margin=dict(
                                    l=0,  # left margin
                                    r=0,  # right margin
                                    b=0,  # bottom margin
                                    t=30,  # top margin
                                    pad=0  # padding
                                ),
                            ),
                    ),
            config=get_buttons_config(),
        )
        return new_graph

    def _create_3d4danimation_figure(self):
        colormap = self.cmap
        data = self.data  # Because it is 3D we assume the spatial coordinates are the last 2
        times, zaxis, lats, lons = get_all_coords(data)
        lats = lats.values
        lons = lons.values

        # n_times = times.values.size
        anim_coord_name = self.get_anim_dim_name()
        coord = data.coords[anim_coord_name.lower()]
        coord_size = coord.size
        anim_buttons = get_update_buttons([anim_coord_name], [coord_size])
        sliders = get_def_slider(anim_coord_name, '', coord_size)
        coords_names = np.array(list(data.coords.keys()))
        coord_idx = np.where(coords_names == anim_coord_name.lower())[0][0]

        data_anim = select_anim_data(data, coord_idx, self.plot_type)

        frames = [go.Frame(data=go.Heatmap(z=data_anim[c_frame,:,:], colorscale=colormap, showscale=False, x=lons, y=lats),
                                  name=f'{anim_coord_name}_{c_frame}',
                                  layout=go.Layout(title=f'{anim_coord_name}: {c_frame}')
                                  ) for c_frame in range(coord_size)]

        new_graph = dcc.Graph(
                id={"type": "figure_anim", "index": self.id},
                figure=go.Figure(
                        data=[go.Heatmap(z=data, colorscale=colormap, showscale=True, x=lons, y=lats)], 
                        layout=go.Layout(title=self.id, 
# zoom, pan, select, lasso, orbit, turntable, zoomInGeo, zoomOutGeo, autoScale2d, resetScale2d, hoverClosestCartesian, hoverClosestGeo, hoverClosestGl2d, hoverClosestPie, toggleHover, resetViews, toggleSpikelines, resetViewMapbox
                                dragmode="pan",
                                autosize=True,
                                xaxis=dict(range=[np.min(lons), np.max(lons)]),
                                yaxis=dict(range=[np.min(lats), np.max(lats)]),
                                height=350,
                                margin=dict(
                                    l=0,  # left margin
                                    r=0,  # right margin
                                    b=0,  # bottom margin
                                    t=30,  # top margin
                                    pad=0  # padding
                                ),
                                updatemenus= [ anim_buttons],
                                sliders= [ sliders ],
                            ),
                        frames=frames
                    ),
            config=get_buttons_config(),
        )
        return new_graph

    def add_child(self, node):
        self.children.append(node)

    def remove_child(self, node):
        self.children.remove(node)

    # --- All the getters
    def get_data(self) -> xr.DataArray:
        return self.data

    def get_parent(self):
        return self.parent

    def get_field_name(self):
        return self.field_name

    def get_bbox(self):
        return self.bbox
    
    def get_spatial_res(self):
        return self.spatial_res
    
    def get_cmap(self):
        return self.cmap

    def get_children(self):
        return self.children
    
    def get_id(self):
        return self.id

    def get_plot_type(self):
        return self.plot_type
    
    def get_anim_dim_name(self) -> str:
        return self.anim_coord_name

    def get_animation_coords(self):
        animation_coords = []
        if self.plot_type.can_request_animation():
            times, zaxis, _, _= get_all_coords(self.data)
            if times.size > 1:
                animation_coords.append(times.dims[0].capitalize())
            if zaxis.size > 1:
                animation_coords.append(zaxis.dims[0].capitalize())

        return animation_coords

    def get_coord_names(self):
        return list(self.data.coords.keys())

    # --- All the setters
    def set_data(self, data):
        self.data = data

    def set_parent(self, parent):
        self.parent = parent

    def set_bbox(self, bbox):
        self.bbox = bbox
    
    def set_spatial_res(self, spatial_res):
        self.spatial_res = spatial_res

    def set_cmap(self, cmap):
        self.cmap = cmap
    
    def set_id(self, id):
        self.id = id

    def set_field_name(self, field_name):
        self.field_name = field_name

    def set_plot_type(self, plot_type):
        self.plot_type = plot_type

    def __str__(self):
        return f'ID: {self.id} BBOX: {self.bbox} Spatial Res: {self.spatial_res}'