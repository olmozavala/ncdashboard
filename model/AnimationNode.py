# This is a the AnimationNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used to animate a model.

import numpy as np
import holoviews as hv
import panel as pn

from model.FigureNode import FigureNode
from model.model_utils import PlotType, Resolutions

class AnimationNode(FigureNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    def __init__(self, id, data, animation_coord, resolution, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.ThreeD_Animation, parent=None,  cmap=None):

        super().__init__(id, data, title=title, field_name=field_name, bbox=bbox, 
                         plot_type=plot_type, parent=parent, cmap=cmap)
        logger.info(f"Created AnimationNode: id={id}, shape={data.shape}, coords={self.coord_names}, cmap={cmap}")

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

        self.anim_coord_name = animation_coord

    # Overloads the create_figure method
    def create_figure(self):
        colormap = self.cmap
        
        # Use simple hv.Dataset conversion to Image, letting HoloViews handle the animation (slider)
        # for xarray.
        # Identify Key Dimensions (kdims) - the animation coordinate
        # Identify Value Dimensions (vdims) - the data
        
        # We assume lat/lon are the last two dimensions
        kdims = [self.anim_coord_name]
        
        ds = hv.Dataset(self.data)
        
        img = ds.to(hv.Image, kdims=kdims, dynamic=True)
        
        img.opts(
            cmap=colormap,
            colorbar=True,
            responsive=True,
            aspect='equal',
            title=self.title or self.id
        )
        
        return img

    def get_anim_dim_name(self) -> str:
        return self.anim_coord_name