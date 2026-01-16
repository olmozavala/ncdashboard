# This is a the FourDNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used plot 4D data.

import holoviews as hv
import geoviews as gv
import cartopy.crs as ccrs
import panel as pn
from holoviews.operation.datashader import rasterize

from model.ThreeDNode import ThreeDNode
from model.model_utils import PlotType, get_all_coords
from loguru import logger

class FourDNode(ThreeDNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st and 2nd dimensions may not be time and depth, we are still calling it like that. 
    def __init__(self, id, data, time_idx, depth_idx, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.FourD, parent=None,  cmap=None):
        super().__init__(id, data, third_coord_idx=time_idx, title=title, field_name=field_name,
                            bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap)
        
        self.depth_idx = depth_idx
        self.depth_coord_name = data.coords[self.coord_names[1]].name
        logger.info(f"Created FourDNode: id={id}, shape={data.shape}, coords={self.coord_names}")

    def _render_plot(self, counter=0, **kwargs):
        colormap = self.cmap
        data = self.data  # Because it is 4D we assume the spatial coordinates are the last 2
        times, zaxis, lats, lons = get_all_coords(data)
        lats = lats.values
        lons = lons.values

        if self.plot_type == PlotType.FourD:
            # We use self.third_coord_idx (from parent) for the first dimension (Time)
            current_slice = data[self.third_coord_idx, self.depth_idx,:,:]

        title = f'{self.title} at {self.coord_names[0].capitalize()} {self.third_coord_idx} and {self.coord_names[1].capitalize()} {self.depth_idx}'
        
        # Use geoviews Image for geographic plotting
        img = gv.Image((lons, lats, current_slice.values), [self.coord_names[-1], self.coord_names[-2]], crs=ccrs.PlateCarree())
        return img.opts(title=title, cmap=colormap)

    def create_figure(self):
        # Return a DynamicMap that updates when update_stream is triggered
        self.dmap = hv.DynamicMap(self._render_plot, streams=[self.update_stream])
        
        # Apply rasterization to the DynamicMap
        # usage of rasterize(dmap) handles zoom/pan coordinate transformation automatically
        rasterized = rasterize(self.dmap).opts(
            cmap=self.cmap,
            tools=['hover'],
            colorbar=True,
            responsive=True,
            aspect='equal'
        )

        # Overlay with tiles
        tiles = gv.tile_sources.OSM()
        return (tiles * rasterized).opts(active_tools=['wheel_zoom', 'pan'])

    def get_stream_source(self):
        if not hasattr(self, 'dmap'):
            self.create_figure()
        return self.dmap

    # Next time and depth functions are used to update the time and depth indices.
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
        # Time controls from parent
        time_controls = super().get_controls()
        
        # Depth controls using helper from parent
        depth_label = self.coord_names[1].capitalize() if len(self.coord_names) > 1 else "Depth"
        depth_controls = self._make_nav_controls(
            self.first_depth, self.prev_depth, self.next_depth, self.last_depth,
            label=depth_label
        )
        
        return pn.Column(time_controls, depth_controls)

