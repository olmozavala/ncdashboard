# This is a the AnimationNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used to animate a model.

import numpy as np
import holoviews as hv
import panel as pn

from model.FigureNode import FigureNode
from model.model_utils import PlotType, Resolutions

import logging
import cartopy.crs as ccrs
import geoviews as gv
from holoviews.operation.datashader import rasterize

logger = logging.getLogger("model.AnimationNode")

# Set tolerance for irregular grids globally for this module
hv.config.image_rtol = 0.01

class AnimationNode(FigureNode):
    def __init__(self, id, data, animation_coord, resolution, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.ThreeD_Animation, parent=None,  cmap=None,
                 x_range=None, y_range=None):

        super().__init__(id, data, title=title, field_name=field_name, bbox=bbox, 
                         plot_type=plot_type, parent=parent, cmap=cmap)
        logger.info(f"Created AnimationNode: id={id}, shape={data.shape}, coords={self.coord_names}, cmap={cmap}")

        self.animation_coord = animation_coord
        self.spatial_res = resolution
        
        # Coarsen the data if necessary for performance
        coarsen = 1
        if resolution == Resolutions.MEDIUM.value:
            coarsen = 4
        if resolution == Resolutions.LOW.value:
            coarsen = 8

        if coarsen > 1:
            data = data.coarsen({self.coord_names[-2]:coarsen, self.coord_names[-1]:coarsen}, 
                                    boundary='trim').mean()

        # We NO LONGER slice the data destructivey. 
        # This prevents the "extent jump" and allows the user to zoom out from the animation.
        self.data = data
        self.anim_coord_name = animation_coord
        
        # Store requested viewport
        self.x_range = x_range
        self.y_range = y_range

        # Initialize Player widget for animation controls
        self.anim_values = self.data[self.anim_coord_name].values
        self.player = pn.widgets.Player(
            name=f'Player {self.id}',
            start=0, end=len(self.anim_values) - 1, value=0,
            loop_policy='loop', interval=500, # Initial speed
            height=60, sizing_mode='stretch_width'
        )

    def _render_frame(self, **kwargs):
        """Callback for DynamicMap to render a single frame of the animation."""
        index = kwargs.get('value', 0)
        
        try:
            val = self.anim_values[index]
            # Select single frame
            frame_data = self.data.sel({self.anim_coord_name: val})
            
            lat_dim = self.coord_names[-2]
            lon_dim = self.coord_names[-1]
            lats = frame_data.coords[lat_dim].values
            lons = frame_data.coords[lon_dim].values
            
            # Create gv.Image
            img = gv.Image((lons, lats, frame_data), [lon_dim, lat_dim], crs=ccrs.PlateCarree())
            
            # Rasterize inside the callback
            return rasterize(img, dynamic=False).opts(
                cmap=self.cmap,
                colorbar=True,
                tools=['hover'],
                responsive=True,
                aspect='equal',
                title=f"{self.title or self.id} - {self.anim_coord_name}: {val}"
            )
        except Exception as e:
            logger.error(f"Error rendering frame {index}: {e}")
            return hv.Text(0, 0, f"Error rendering frame: {e}")

    # Overloads the create_figure method
    def create_figure(self):
        logger.info(f"Creating dynamic animation for {self.id}...")
        
        # Link player to the DynamicMap
        stream = hv.streams.Params(self.player, ['value'])
        self.dmap = hv.DynamicMap(self._render_frame, streams=[stream])
        
        # Add tiles 
        tiles = gv.tile_sources.OSM()
        
        # Apply layout options
        plot = (tiles * self.dmap).opts(
            active_tools=['wheel_zoom', 'pan'],
            responsive=True,
            aspect='equal',
            title=self.title or self.id
        )

        # Set initial viewport if requested
        if self.x_range and self.y_range:
            # We apply xlim/ylim to match the parent viewport.
            # HoloViews/Geoviews will handle the coordinate system matching (meters vs degrees)
            # as long as we apply it to the final projected overlay.
            plot = plot.opts(xlim=self.x_range, ylim=self.y_range)
            logger.info(f"Applied initial viewport: {self.x_range}, {self.y_range}")

        return plot

    def get_controls(self):
        """Returns the player widget as navigation controls."""
        return pn.Row(pn.layout.HSpacer(), self.player, pn.layout.HSpacer(), height=80)

    def get_anim_dim_name(self) -> str:
        return self.anim_coord_name