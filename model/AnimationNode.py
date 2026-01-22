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

class AnimationNode(FigureNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    def __init__(self, id, data, animation_coord, resolution, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.ThreeD_Animation, parent=None,  cmap=None,
                 x_range=None, y_range=None):

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
            data = data.coarsen({self.coord_names[-2]:coarsen, self.coord_names[-1]:coarsen}, 
                                    boundary='trim').mean()

        # Crop data if ranges provided (transforming from Mercator to PlateCarree)
        self.data = self._crop_data(data, x_range, y_range)
        self.anim_coord_name = animation_coord
        
        # Initialize Player widget for animation controls
        self.anim_values = self.data[self.anim_coord_name].values
        self.player = pn.widgets.Player(
            name=f'Player {self.id}',
            start=0, end=len(self.anim_values) - 1, value=0,
            loop_policy='loop', interval=500, # Initial speed
            height=60, sizing_mode='stretch_width'
        )

    def _crop_data(self, data, x_range, y_range):
        """Crops the data to the specified Web Mercator ranges."""
        if x_range is None or y_range is None:
            return data
            
        try:
            # Transform Web Mercator ranges to PlateCarree (Data CRS)
            x0, y0 = ccrs.PlateCarree().transform_point(x_range[0], y_range[0], ccrs.GoogleTiles())
            x1, y1 = ccrs.PlateCarree().transform_point(x_range[1], y_range[1], ccrs.GoogleTiles())
            
            # Identify lat/lon dims
            lat_dim = self.coord_names[-2]
            lon_dim = self.coord_names[-1]

            # Ensure min/max ordering for slicing
            min_lon, max_lon = sorted([x0, x1])
            min_lat, max_lat = sorted([y0, y1])

            logger.info(f"Cropping animation to: Lon({min_lon:.2f}, {max_lon:.2f}), Lat({min_lat:.2f}, {max_lat:.2f})")
            return data.sel({lon_dim: slice(min_lon, max_lon), lat_dim: slice(min_lat, max_lat)})
            
        except Exception as e:
            logger.error(f"Failed to crop data: {e}")
            return data

    def _render_frame(self, **kwargs):
        """Callback for DynamicMap to render a single frame of the animation."""
        # HoloViews passes stream values as keyword arguments
        index = kwargs.get('value', 0)
        
        try:
            val = self.anim_values[index]
            logger.info(f"Rendering frame index {index} (val={val}) for {self.id}")
            
            # Select single frame
            frame_data = self.data.sel({self.anim_coord_name: val})
            
            lat_dim = self.coord_names[-2]
            lon_dim = self.coord_names[-1]
            lats = frame_data.coords[lat_dim].values
            lons = frame_data.coords[lon_dim].values
            
            # Create gv.Image
            img = gv.Image((lons, lats, frame_data), [lon_dim, lat_dim], crs=ccrs.PlateCarree())
            
            # Rasterize inside the callback with dynamic=False to return a static element.
            return rasterize(img, dynamic=False).opts(
                cmap=self.cmap,
                colorbar=True,
                tools=['hover'],
                title=f"{self.title or self.id} - {self.anim_coord_name}: {val}"
            )
        except Exception as e:
            logger.error(f"Error rendering frame {index}: {e}")
            return hv.Text(0, 0, f"Error rendering frame: {e}")

    # Overloads the create_figure method
    def create_figure(self):
        logger.info(f"Creating dynamic animation for {self.id}...")
        
        # Explicitly link player.param.value to the DynamicMap using a Params stream
        # This is more robust in Panel/HoloViews applications
        stream = hv.streams.Params(self.player, ['value'])
        self.dmap = hv.DynamicMap(self._render_frame, streams=[stream])
        
        # Add tiles and options
        tiles = gv.tile_sources.OSM()
        
        return (tiles * self.dmap).opts(
            active_tools=['wheel_zoom', 'pan'],
            title=self.title or self.id
        )

    def get_controls(self):
        """Returns the player widget as navigation controls."""
        return pn.Row(pn.layout.HSpacer(), self.player, pn.layout.HSpacer(), height=80)

    def get_anim_dim_name(self) -> str:
        return self.anim_coord_name