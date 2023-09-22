
# This is a the FourDNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used plot 4D data.

import plotly.graph_objects as go
from dash import dcc
from model.ThreeDNode import ThreeDNode

from model.model_utils import PlotType, get_all_coords
from proj_layout.utils import get_buttons_config

class FourDNode(ThreeDNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st and 2nd dimensions may not be time and depth, we are still calling it like that. 
    def __init__(self, id, data, time_idx, depth_idx, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.FourD, parent=None,  cmap=None):
        super().__init__(id, data, time_idx, title=title, field_name=field_name,
                            bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap)
        
        self.depth_idx = depth_idx
        self.depth_coord_name = data.coords[self.coord_names[1]].name

    def create_figure(self):
        colormap = self.cmap
        data = self.data  # Because it is 3D we assume the spatial coordinates are the last 2
        times, zaxis, lats, lons = get_all_coords(data)
        lats = lats.values
        lons = lons.values

        print(f"Time: {self.time_idx}, Depth: {self.depth_idx}")  
        if self.plot_type == PlotType.FourD:
            data = data[self.time_idx, self.depth_idx,:,:]

        title = f'{self.title}:{self.id} at {self.coord_names[0]} {self.time_idx} and {self.coord_names[1]} {self.depth_idx}'
        new_graph = dcc.Graph(
                id={"type": "figure", "index": self.id},
                figure=go.Figure(
                        data=[go.Heatmap(z=data, colorscale=colormap, showscale=True, x=lons, y=lats)], 
                        layout=go.Layout(title=title, 
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

    # Next time and depth functions are used to update the time and depth indices.
    def next_depth(self):
        self.depth_idx = (self.depth_idx + 1) % len(self.data[self.depth_coord_name])
        return self.depth_idx
    
    def prev_depth(self):
        self.depth_idx = (self.depth_idx - 1) % len(self.data[self.depth_coord_name])
        return self.depth_idx

    def set_depth_idx(self, depth_idx):
        self.depth_idx = depth_idx
   
    def get_depth_idx(self):
        return self.depth_idx

