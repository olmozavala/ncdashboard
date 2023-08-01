# An enum with the types of plots
from enum import Enum
from model.model_utils import PlotType, get_all_coords, select_anim_data
import plotly.graph_objects as go
from dash import dcc
import xarray as xr
import numpy as np

from proj_layout.utils import get_buttons_config, get_def_slider, get_update_buttons, select_colormap

class TreeNode:
    def __init__(self, id, data, field_name=None, bbox=None, spatial_res=None, 
                 plot_type = PlotType.TwoD, parent=None,  cmap=None, animation=False, 
                 anim_coord_name=None):
        self.parent = parent
        self.id = id
        self.bbox = bbox
        self.spatial_res = spatial_res
        self.children = []
        self.field_name = field_name
        self.data = data
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
        if self.plot_type == PlotType.ThreeD or self.plot_type == PlotType.FourD:
            return self._create_3d4d_figure()
        if self.plot_type == PlotType.ThreeD_Animation or self.plot_type == PlotType.FourD_Animation:
            return self._create_3d4danimation_figure()

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
                id=self.id,
                figure=go.Figure(
                        data=[go.Heatmap(z=data, colorscale=colormap, showscale=True, x=lons, y=lats)], 
                        layout=go.Layout(title="Imshow", 
                                dragmode="zoom",
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
                id=self.id,
                figure=go.Figure(
                        data=[go.Heatmap(z=data, colorscale=colormap, showscale=True, x=lons, y=lats)], 
                        layout=go.Layout(title="Imshow", 
                                dragmode="zoom",
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


    #     new_graph = dcc.Graph(
    #             id=id,
    #             figure=go.Figure(
    #                     data=[go.Heatmap(z=data[0, 0,:,:], colorscale=colormap, showscale=True, x=lons, y=lats)], 
    #                     layout=go.Layout(title="Imshow", 
    #                             dragmode="zoom",
    #                             height=800,
    #                             updatemenus= [ get_update_buttons([anim_coord_name, dim4_name], [n_dim3, n_dim4]) ],
    #                             sliders= [ get_def_slider(anim_coord_name, '', n_dim3), get_def_slider(dim4_name, '', n_dim4)],
    #                         ),
    #                             [go.Frame(data=go.Heatmap(z=data[0,c_depth,:], colorscale=colormap, showscale=False, x=lons, y=lats),
    #                               name=f'{dim4_name}_{c_depth}',
    #                               layout=go.Layout(title=f'{dim4_name}: {c_depth}')
    #                               ) for c_depth in range(n_dim4)] 
    #                 ),
    #         config=get_buttons_config(),
    #     )
    #     return new_graph


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

    # --- All the setters
    def get_animation_coords(self):
        animation_coords = []
        if self.plot_type.can_request_animation():
            times, zaxis, _, _= get_all_coords(self.data)
            if times.size > 1:
                animation_coords.append(times.dims[0].capitalize())
            if zaxis.size > 1:
                animation_coords.append(zaxis.dims[0].capitalize())

        return animation_coords

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