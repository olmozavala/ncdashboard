# This is a the OneDNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used plot 1D data.

import numpy as np
import holoviews as hv
import panel as pn

from model.FigureNode import FigureNode
from model.model_utils import PlotType, get_all_coords
from loguru import logger


class OneDNode(FigureNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st dimensions may not be time, we are still calling it like that. 
    def __init__(self, id, data, title=None, field_name=None, 
                 bbox=None, plot_type=PlotType.OneD, parent=None, **params):

        super().__init__(id, data, title=title, field_name=field_name, 
                         bbox=bbox, plot_type=plot_type, parent=parent, **params)
        logger.info(f"Created OneDNode: id={id}, shape={data.shape}, coords={self.coord_names}")

    def create_figure(self):
        dims = self.data.dims  # Get the list of dimensions
        profile = self.data.values  # Get the values of the data
        x_vals = list(range(len(profile)))

        # Get the units of the coordinate
        try:
            units_y = self.data.units
        except:
            units_y = 'no units'

        # Create HoloViews curve
        curve = hv.Curve((x_vals, profile), 'Index', f'{self.long_name} ({self.units})')
        scatter = hv.Scatter((x_vals, profile))
        
        plot = (curve * scatter).opts(
            title=self.title,
            responsive=True,
            height=350,
            show_grid=True
        )
        return plot