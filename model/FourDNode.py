# This is a the FourDNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used plot 4D data.

import holoviews as hv
from model.ThreeDNode import ThreeDNode
from model.model_utils import PlotType, get_all_coords
from loguru import logger

class FourDNode(ThreeDNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st and 2nd dimensions may not be time and depth, we are still calling it like that. 
    def __init__(self, id, data, time_idx, depth_idx, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.FourD, parent=None,  cmap=None):
        super().__init__(id, data, coord_idx=time_idx, title=title, field_name=field_name,
                            bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap)
        
        self.depth_idx = depth_idx
        self.depth_coord_name = data.coords[self.coord_names[1]].name
        logger.info(f"Created FourDNode: id={id}, shape={data.shape}, coords={self.coord_names}")

    def create_figure(self):
        colormap = self.cmap
        data = self.data  # Because it is 4D we assume the spatial coordinates are the last 2
        times, zaxis, lats, lons = get_all_coords(data)
        lats = lats.values
        lons = lons.values

        if self.plot_type == PlotType.FourD:
            # We use self.coord_idx (from parent) for the first dimension (Time)
            current_slice = data[self.coord_idx, self.depth_idx,:,:]

        title = f'{self.title} at {self.coord_names[0].capitalize()} {self.coord_idx} and {self.coord_names[1].capitalize()} {self.depth_idx}'
        
        img = hv.Image((lons, lats, current_slice), [self.coord_names[-1], self.coord_names[-2]])
        img.opts(
            cmap=colormap,
            title=title,
            tools=['hover'],
            colorbar=True,
            responsive=True,
            aspect='equal'
        )
        return img

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

