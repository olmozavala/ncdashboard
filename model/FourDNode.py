# FourDNode class — inherits from ThreeDNode to add a 4th dimension (depth).

import holoviews as hv
import geoviews as gv
import cartopy.crs as ccrs
import panel as pn
from holoviews.operation.datashader import rasterize

from model.ThreeDNode import ThreeDNode
from model.model_utils import PlotType, get_all_coords
from loguru import logger

class FourDNode(ThreeDNode):
    def __init__(self, id, data, time_idx, depth_idx, title=None, field_name=None, 
                 bbox=None, plot_type=PlotType.FourD, parent=None, cmap=None, **params):
        super().__init__(id, data, time_idx, title=title, field_name=field_name,
                            bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap, **params)
        
        self.depth_idx = depth_idx
        self.depth_coord_name = data.coords[self.coord_names[1]].name
        logger.info(f"Created FourDNode: id={id}, shape={data.shape}, coords={self.coord_names}")

    def _animate_callback(self, animation_coord, data=None):
        """Overrides animation callback to slice 4D data into 3D before animation."""
        sliced_data = self.data
        
        if animation_coord == self.coord_names[0]:  # Animating Time
             depth_dim = self.coord_names[1]
             sliced_data = self.data.isel({depth_dim: self.depth_idx})
             logger.info(f"Animating Time. Sliced Depth at index {self.depth_idx}. New shape: {sliced_data.shape}")
             
        elif animation_coord == self.coord_names[1]:  # Animating Depth
             time_dim = self.coord_names[0]
             sliced_data = self.data.isel({time_dim: self.third_coord_idx})
             logger.info(f"Animating Depth. Sliced Time at index {self.third_coord_idx}. New shape: {sliced_data.shape}")
        
        super()._animate_callback(animation_coord, data=sliced_data)

    def _render_plot(self, counter=0, **kwargs):
        data = self.data
        times, zaxis, lats, lons = get_all_coords(data)
        lats = lats.values
        lons = lons.values

        if self.plot_type == PlotType.FourD:
            current_slice = data[self.third_coord_idx, self.depth_idx, :, :]

        title = f'{self.title} at {self.coord_names[0].capitalize()} {self.third_coord_idx} and {self.coord_names[1].capitalize()} {self.depth_idx}'
        
        vdims = [hv.Dimension(self.field_name, label=self.label)]
        img = gv.Image((lons, lats, current_slice.values), [self.coord_names[-1], self.coord_names[-2]], 
                       vdims=vdims, crs=ccrs.PlateCarree())
        return img.opts(title=title)

    def create_figure(self):
        # Only time/depth index changes and range changes trigger re-rendering of the data
        self.dmap = hv.DynamicMap(self._render_plot, 
                                  streams=[self.update_stream, self.range_stream])
        
        # We apply visual updates (cmap/clim/cnorm) reactively using .apply.opts()
        # This prevents the viewport from resetting when colors change.
        rasterized = rasterize(self.dmap, width=800, pixel_ratio=2).apply.opts(
            cmap=self.param.cmap,
            clim=self.param.clim,
            cnorm=self.param.cnorm,
            colorbar=True,
            responsive=True,
            aspect='equal'
        )
        
        self.range_stream.source = rasterized

        # Build the geo overlay using the shared helper
        return self._build_geo_overlay(rasterized, responsive=True, aspect='equal')

    def next_depth(self):
        self.depth_idx = (self.depth_idx + 1) % len(self.data[self.depth_coord_name])
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.depth_idx
    
    def prev_depth(self):
        self.depth_idx = (self.depth_idx - 1) % len(self.data[self.depth_coord_name])
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.depth_idx

    def first_depth(self):
        self.depth_idx = 0
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.depth_idx

    def last_depth(self):
        self.depth_idx = len(self.data[self.depth_coord_name]) - 1
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.depth_idx

    def set_depth_idx(self, depth_idx):
        self.depth_idx = depth_idx
        self.update_stream.event(counter=self.update_stream.counter + 1)
    
    def get_depth_idx(self):
        return self.depth_idx
    
    def get_controls(self):
        label = self.coord_names[0].capitalize() if len(self.coord_names) > 0 else "Slice"
        time_controls = self._make_nav_controls(
            self.first_slice, self.prev_slice, self.next_slice, self.last_slice,
            label=label,
            anim_coord=self.coord_names[0]
        )
        
        depth_label = self.coord_names[1].capitalize() if len(self.coord_names) > 1 else "Depth"
        depth_controls = self._make_nav_controls(
            self.first_depth, self.prev_depth, self.next_depth, self.last_depth,
            label=depth_label,
            anim_coord=self.coord_names[1]
        )
        
        return pn.Column(time_controls, depth_controls)
