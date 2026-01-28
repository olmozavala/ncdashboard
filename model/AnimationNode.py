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

        # Crop data if ranges provided for performance, but with a buffer
        self.data = self._crop_data(data, x_range, y_range)
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

    def _crop_data(self, data, x_range, y_range):
        """Crops the data to the specified ranges with a small buffer."""
        if x_range is None or y_range is None:
            return data
            
        try:
            # Determine if ranges are in degrees (PlateCarree) or meters (Mercator)
            min_lon, max_lon = sorted([x_range[0], x_range[1]])
            min_lat, max_lat = sorted([y_range[0], y_range[1]])

            # If values are large, they are likely Mercator/WebMercator meters.
            if abs(min_lon) > 500 or abs(min_lat) > 90:
                logger.info("Ranges in meters (Mercator), transforming to PlateCarree (degrees) for slicing...")
                src_crs = ccrs.Mercator()
                dest_crs = ccrs.PlateCarree()
                x0, y0 = dest_crs.transform_point(x_range[0], y_range[0], src_crs)
                x1, y1 = dest_crs.transform_point(x_range[1], y_range[1], src_crs)
                min_lon, max_lon = sorted([x0, x1])
                min_lat, max_lat = sorted([y0, y1])
            else:
                logger.info("Ranges appear to be in degrees. No transformation needed for slicing.")

            # Add 20% buffer to the cropped data for local panning
            lon_buffer = (max_lon - min_lon) * 0.2
            lat_buffer = (max_lat - min_lat) * 0.2
            
            # Identify lat/lon dims
            lat_dim = self.coord_names[-2]
            lon_dim = self.coord_names[-1]

            logger.info(f"Cropping data with buffer: Lon({min_lon-lon_buffer:.2f}, {max_lon+lon_buffer:.2f}), Lat({min_lat-lat_buffer:.2f}, {max_lat+lat_buffer:.2f})")
            
            # Handle descending latitudes if necessary (common in netCDF)
            lats = data[lat_dim].values
            if lats[0] > lats[-1]:
                lat_slice = slice(max_lat + lat_buffer, min_lat - lat_buffer)
            else:
                lat_slice = slice(min_lat - lat_buffer, max_lat + lat_buffer)
                
            return data.sel({lon_dim: slice(min_lon - lon_buffer, max_lon + lon_buffer), 
                             lat_dim: lat_slice})
            
        except Exception as e:
            logger.error(f"Failed to crop data: {e}")
            return data

    def _render_frame(self, **kwargs):
        """Callback for DynamicMap to render a single frame of the animation."""
        index = kwargs.get('value', 0)
        
        try:
            val = self.anim_values[index]
            # Select single frame with nearest method for safety with floats
            frame_data = self.data.sel({self.anim_coord_name: val}, method='nearest')
            
            lat_dim = self.coord_names[-2]
            lon_dim = self.coord_names[-1]
            lats = frame_data.coords[lat_dim].values
            lons = frame_data.coords[lon_dim].values
            
            # Create gv.Image with explicit coords tuple for stability
            img = gv.Image((lons, lats, frame_data.values), [lon_dim, lat_dim], crs=ccrs.PlateCarree())
            
            # Rasterize inside the callback with dynamic=False
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
            try:
                min_lon, max_lon = sorted([self.x_range[0], self.x_range[1]])
                min_lat, max_lat = sorted([self.y_range[0], self.y_range[1]])

                # If the values are small (degrees), transform to Web Mercator meters for the plot
                if abs(min_lon) <= 180 and abs(min_lat) <= 90:
                    from holoviews.util.transform import lon_lat_to_easting_northing
                    logger.info(f"Transforming degrees viewport to meters...")
                    x0, y0 = lon_lat_to_easting_northing(self.x_range[0], self.y_range[0])
                    x1, y1 = lon_lat_to_easting_northing(self.x_range[1], self.y_range[1])
                    final_xlim = tuple(sorted([x0, x1]))
                    final_ylim = tuple(sorted([y0, y1]))
                else:
                    final_xlim = (min_lon, max_lon)
                    final_ylim = (min_lat, max_lat)

                plot = plot.opts(xlim=final_xlim, ylim=final_ylim)
                logger.info(f"Viewport locked to (meters): {final_xlim}, {final_ylim}")
            except Exception as e:
                logger.error(f"Failed to set initial viewport: {e}")

        return plot

    def get_controls(self):
        """Returns the player widget as navigation controls."""
        return pn.Row(pn.layout.HSpacer(), self.player, pn.layout.HSpacer(), height=80)

    def get_anim_dim_name(self) -> str:
        return self.anim_coord_name