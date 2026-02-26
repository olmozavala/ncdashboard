# AnimationNode — animates through a coordinate dimension with pre-rendered frames.

import numpy as np
import holoviews as hv
import panel as pn

from model.FigureNode import FigureNode
from model.model_utils import PlotType, Resolutions

import cartopy.crs as ccrs
import geoviews as gv
from holoviews.operation.datashader import rasterize
from loguru import logger

# Set tolerance for irregular grids so Image does not warn
hv.config.image_rtol = 0.1

class AnimationNode(FigureNode):
    def __init__(self, id, data, animation_coord, resolution, title=None, field_name=None, 
                 bbox=None, plot_type=PlotType.ThreeD_Animation, parent=None, cmap=None,
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
            data = data.coarsen({self.coord_names[-2]: coarsen, self.coord_names[-1]: coarsen}, 
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
            loop_policy='loop', interval=500,
            height=60, sizing_mode='stretch_width',
            show_loop_controls=False
        )

        # --- Caching and Pre-rendering ---
        self._cache = {}
        self._is_alive = True
        
        # Start background pre-rendering
        import threading
        self._pre_render_thread = threading.Thread(target=self._run_pre_render, daemon=True)
        self._pre_render_thread.start()

    def _run_pre_render(self):
        """Background thread to pre-populate the cache with rasterized frames."""
        logger.info(f"Pre-rendering started for {self.id}")
        for i in range(len(self.anim_values)):
            if not self._is_alive:
                break
            try:
                if i not in self._cache:
                    self._get_frame(i)
            except Exception as e:
                logger.error(f"Pre-render error at index {i}: {e}")
        logger.info(f"Pre-rendering completed for {self.id}")

    def __del__(self):
        self._is_alive = False

    def _get_frame(self, index):
        """Internal method to get or compute a specific frame."""
        if index in self._cache:
            return self._cache[index]

        val = self.anim_values[index]
        
        # Use isel() for integer/index-based coordinates (e.g. WRF's 'Time' dimension
        # which has no real coordinate values, just 0,1,2,...).
        # sel(method='nearest') on such coords causes xarray to embed
        # {'method': 'nearest'} in the result's metadata, which HoloViews
        # then tries to use as a format-string key → KeyError.
        coord_vals = self.data[self.anim_coord_name].values
        coord_is_index = np.issubdtype(coord_vals.dtype, np.integer)
        
        if coord_is_index:
            frame_data = self.data.isel({self.anim_coord_name: index})
        else:
            frame_data = self.data.sel({self.anim_coord_name: val}, method='nearest')

        
        from model.model_utils import get_all_coords
        _, _, lats_coord, lons_coord = get_all_coords(frame_data)
        
        lat_vals = lats_coord.values
        lon_vals = lons_coord.values
        
        if lat_vals.ndim > 1:
            lat_vals = lat_vals[:, 0]
        if lon_vals.ndim > 1:
            lon_vals = lon_vals[0, :]
        
        # Format value for title
        if isinstance(val, (float, np.float32, np.float64)):
            val_str = f"{val:.2f}"
        else:
            val_str = str(val)

        title = self._safe_title(f"{self.title or self.id} - [{index}] {self.anim_coord_name}: {val_str}")
        
        vdims = [hv.Dimension(self.field_name, label=self.label)]
        
        lat_name = lats_coord.name if lats_coord.name else self.coord_names[-2]
        lon_name = lons_coord.name if lons_coord.name else self.coord_names[-1]

        # Use QuadMesh for curvilinear grids (e.g. WRF), Image otherwise
        if lat_vals.ndim > 1 or lon_vals.ndim > 1:
            img = gv.QuadMesh((lons_coord, lats_coord, frame_data.values), [lon_name, lat_name],
                              vdims=vdims, crs=ccrs.PlateCarree())
        else:
            img = gv.Image((lon_vals, lat_vals, frame_data.values), [lon_name, lat_name], 
                           vdims=vdims, crs=ccrs.PlateCarree())
        
        self._cache[index] = img
        return img

    def _crop_data(self, data, x_range, y_range):
        """Crops the data to the specified ranges with a small buffer."""
        if x_range is None or y_range is None:
            return data
            
        try:
            min_lon, max_lon = sorted([x_range[0], x_range[1]])
            min_lat, max_lat = sorted([y_range[0], y_range[1]])

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

            lon_buffer = (max_lon - min_lon) * 0.2
            lat_buffer = (max_lat - min_lat) * 0.2
            
            lat_dim = self.coord_names[-2]
            lon_dim = self.coord_names[-1]

            logger.info(f"Cropping data with buffer: Lon({min_lon-lon_buffer:.2f}, {max_lon+lon_buffer:.2f}), Lat({min_lat-lat_buffer:.2f}, {max_lat+lat_buffer:.2f})")
            
            lats = data[lat_dim].values
            if len(lats) > 1 and lats[0] > lats[-1]:
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
            img = self._get_frame(index)
            
            # Recalculate title for the specific frame
            val = self.anim_values[index]
            if isinstance(val, (float, np.float32, np.float64)):
                val_str = f"{val:.2f}"
            else:
                val_str = str(val)
            title = self._safe_title(f"{self.title or self.id} - [{index}] {self.anim_coord_name}: {val_str}")
            self.title_val = title
            
            # Return styled image. Rasterize is applied at the top level.
            return img.opts()
        except Exception as e:
            logger.error(f"Error rendering frame {index}: {e}")
            # Return an empty image instead of Text to avoid colorbar errors
            lat_dim = self.coord_names[-2]
            lon_dim = self.coord_names[-1]
            empty_data = np.zeros((2, 2))
            return gv.Image(([0, 1], [0, 1], empty_data), [lon_dim, lat_dim], crs=ccrs.PlateCarree()).opts(title=f"Error: {e}")

    def create_figure(self):
        logger.info(f"Creating dynamic animation for {self.id}...")
        
        player_stream = hv.streams.Params(self.player, ['value'])
        param_stream = hv.streams.Params(self, ['cmap', 'clim'])
        self.dmap = hv.DynamicMap(self._render_frame, streams=[player_stream, param_stream])
        
        # Wrap in rasterize: it will render the data into an image server-side
        self.rasterized = rasterize(self.dmap, pixel_ratio=2).apply.opts(
            alpha=0.8,
            cmap=self.param.cmap,
            clim=self.param.clim,
            title=self.param.title_val,
            colorbar=True,
            responsive=True,
            shared_axes=False,
            default_tools=self.DEFAULT_TOOLS,
            tools=self.GEO_TOOLS,
            active_tools=self.GEO_ACTIVE_TOOLS
        )
        
        tiles = gv.tile_sources.OSM()

        plot = (tiles * self.rasterized)

        # Set initial viewport if requested
        if self.x_range and self.y_range:
            try:
                min_lon, max_lon = sorted([self.x_range[0], self.x_range[1]])
                min_lat, max_lat = sorted([self.y_range[0], self.y_range[1]])

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

        # Add click markers and wheel_zoom hook using shared helpers
        marker_dmap = self._build_marker_overlay()
        return (plot * marker_dmap)

    def get_controls(self):
        """Returns the player widget as navigation controls."""
        return pn.Row(pn.layout.HSpacer(), self.player, pn.layout.HSpacer(), height=80)

    def get_anim_dim_name(self) -> str:
        return self.anim_coord_name