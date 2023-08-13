# This is a the AnimationNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used to animate a model.

import numpy as np
import plotly.graph_objects as go
from dash import dcc

from model.TreeNode import FigureNode
from model.model_utils import PlotType, Resolutions
from model.model_utils import PlotType, get_all_coords, select_anim_data
from proj_layout.utils import get_buttons_config, get_def_slider, get_update_buttons, select_colormap


class AnimationNode(FigureNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    def __init__(self, id, data, animation_coord, resolution, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.ThreeD_Animation, parent=None,  cmap=None):

        super().__init__(id, data, title=title, field_name=field_name, bbox=bbox, 
                         plot_type=plot_type, parent=parent, cmap=cmap)

        self.animation_coord = animation_coord
        self.spatial_res = resolution
        
        # Coarsen the data if necessary
        coarsen = 1
        if resolution == Resolutions.MEDIUM.value:
            coarsen = 4
        if resolution == Resolutions.LOW.value:
            coarsen = 8

        if coarsen > 1:
            self.data = data.coarsen({self.coord_names[-2]:coarsen, self.coord_names[-1]:coarsen}, 
                                    boundary='trim').mean()
        else:
            self.data = data

        # ----------- Only used if it is an animation (TODO move to another class)
        self.anim_coord_name = animation_coord

    # Overloads the create_figure method
    def create_figure(self):
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


    def get_anim_dim_name(self) -> str:
        return self.anim_coord_name