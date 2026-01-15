# This is a the ThreeDNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used plot 4D data.

import holoviews as hv
import panel as pn

from model.TreeNode import FigureNode
from model.model_utils import PlotType, get_all_coords

class ThreeDNode(FigureNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st dimensions may not be time, we are still calling it like that. 
    def __init__(self, id, data, time_idx, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.FourD, parent=None,  cmap=None):

        super().__init__(id, data, title=title, field_name=field_name, bbox=bbox, 
                         plot_type=plot_type, parent=parent, cmap=cmap)

        self.time_idx = time_idx
        self.time_coord_name = data.coords[self.coord_names[0]].name

    def create_figure(self):
        colormap = self.cmap
        
        data = self.data
        if self.plot_type == PlotType.ThreeD:
            # We assume logical structure [time, lat, lon] for 3D
            # Select the time slice
            data = self.data[self.time_idx, :, :]

        # We assume the last two coordinates are spatial (lat, lon)
        lats = data.coords[self.coord_names[-2]].values
        lons = data.coords[self.coord_names[-1]].values

        title = f'{self.title} at {self.coord_names[0].capitalize()} {self.time_idx}'

        img = hv.Image((lons, lats, data), [self.coord_names[-1], self.coord_names[-2]])
        img.opts(
            cmap=colormap,
            title=title,
            tools=['hover'],
            colorbar=True,
            responsive=True,
            aspect='equal'
        )
        return img

    def next_time(self):
        self.time_idx = (self.time_idx + 1) % len(self.data[self.coord_names[0]])
        return self.time_idx
    
    def prev_time(self):
        self.time_idx = (self.time_idx - 1) % len(self.data[self.coord_names[0]])
        return self.time_idx

    def set_time_idx(self, time_idx):
        self.time_idx = time_idx
        
    def get_time_idx(self):
        return self.time_idx
