#Similar to AnimationNode, its a class that inherits from TreeNode. In this case it manages
# figures that will generate a profile plot. 


import numpy as np
import holoviews as hv
import panel as pn

from model.FigureNode import FigureNode
from model.model_utils import PlotType, Resolutions


from loguru import logger

class ProfileNode(FigureNode):

    def __init__(self, id, data, lat, lon, dim_prof, title=None, field_name=None, 
                 bbox=None, plot_type=PlotType.Profile, parent=None):

        super().__init__(id, data, title=title, field_name=field_name, bbox=bbox, 
                         plot_type=plot_type, parent=parent)

        self.lat = lat
        self.lon = lon
        self.dim_prof = dim_prof
        logger.info(f"Created ProfileNode: id={id}, lat={lat}, lon={lon}, dim={dim_prof}, shape={data.shape}")

    def create_figure(self):
        
        dims = self.data.dims  # Get the list of dimensions
        profile = self.data.values  # Get the values of the data
        coordinate = self.data.coords[self.dim_prof]  # Get the coordinate

        # Get the units of the coordinate
        try:
            units_y = coordinate.units
        except:
            units_y = 'no units'

        # Flip valid for Depth (if positive)
        # We can handle this via invert_yaxis in options or modifying data
        vals = coordinate.values
        if self.dim_prof.lower() == 'depth' and len(vals) > 1:
             if vals[1] > vals[0]:
                 # Inverted depth-like coordinate
                 vals = -vals

        # Create Curve
        # x is profile value, y is depth/elevation (coordinate)
        # Or standard profile: Depth on Y, Value on X
        # Original code:
        # if depth: x=profile, y=coordinate (depth)
        # else: x=coordinate, y=profile
        
        if self.dim_prof.lower() == 'depth':
            curve = hv.Curve((profile, vals), f'{self.long_name} ({self.units})', f'{dims[-1].capitalize()} ({units_y})')
            scatter = hv.Scatter((profile, vals))
        else:
            curve = hv.Curve((vals, profile), f'{dims[-1].capitalize()} ({units_y})', f'{self.long_name} ({self.units})')
            scatter = hv.Scatter((vals, profile))

        plot = (curve * scatter).opts(
            title=self.title,
            tools=self.GEO_TOOLS,
            active_tools=self.GEO_ACTIVE_TOOLS,
            default_tools=self.DEFAULT_TOOLS,
            responsive=True,
            height=350,
            show_grid=True,
            shared_axes=False
        )
        return plot


