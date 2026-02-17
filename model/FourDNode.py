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
import param

class FourDNode(ThreeDNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st and 2nd dimensions may not be time and depth, we are still calling it like that. 
    def __init__(self, id, data, time_idx, depth_idx, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.FourD, parent=None,  cmap=None, **params):
        super().__init__(id, data, time_idx, title=title, field_name=field_name,
                            bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap, **params)
        
        self.depth_idx = depth_idx
        self.depth_coord_name = data.coords[self.coord_names[1]].name
        logger.info(f"Created FourDNode: id={id}, shape={data.shape}, coords={self.coord_names}")

    def _animate_callback(self, animation_coord, data=None):
        """
        Overrides animation callback to slice 4D data into 3D before animation.
        """
        # Data structure: [Time, Depth, Lat, Lon]
        # self.coord_names[0] is Time (third_coord_idx)
        # self.coord_names[1] is Depth (depth_idx)
        
        sliced_data = self.data
        
        if animation_coord == self.coord_names[0]: # Animating Time
             # Fix Depth to current index
             depth_dim = self.coord_names[1]
             # Select returns a new dataset with that dimension removed (if drop=True which is default for simple index selection in xarray? No, wait)
             # .isel(depth=0) reduces dimension.
             sliced_data = self.data.isel({depth_dim: self.depth_idx})
             logger.info(f"Animating Time. Sliced Depth at index {self.depth_idx}. New shape: {sliced_data.shape}")
             
        elif animation_coord == self.coord_names[1]: # Animating Depth
             # Fix Time to current index
             time_dim = self.coord_names[0]
             sliced_data = self.data.isel({time_dim: self.third_coord_idx})
             logger.info(f"Animating Depth. Sliced Time at index {self.third_coord_idx}. New shape: {sliced_data.shape}")
        
        # Call parent with sliced data
        super()._animate_callback(animation_coord, data=sliced_data)

    def _render_plot(self, counter=0, **kwargs):
        colormap = self.cmap
        data = self.data  # Because it is 4D we assume the spatial coordinates are the last 2
        times, zaxis, lats, lons = get_all_coords(data)
        lats = lats.values
        lons = lons.values

        current_slice = data[self.third_coord_idx, self.depth_idx,:,:]

        # Retrieve params from kwargs (stream) or self (fallback)
        cmap = kwargs.get('cmap_val', self.cmap)
        clim = kwargs.get('clim_val', self.clim)

        title = f'{self.title} at {self.coord_names[0].capitalize()} {self.third_coord_idx} and {self.coord_names[1].capitalize()} {self.depth_idx}'
        
        # Use geoviews Image for geographic plotting
        vdims = [hv.Dimension(self.field_name, label=self.label)]
        # We set a unique group to prevent collision in the Panel/Bokeh rendering pipeline
        group_name = f"Group_{self.id}"
        img = gv.Image((lons, lats, current_slice.values), [self.coord_names[-1], self.coord_names[-2]], 
                       vdims=vdims, crs=ccrs.PlateCarree(), group=group_name)

        return img.opts(title=title, cmap=cmap, clim=clim)

    def create_figure(self):
        # Create a stream that watches for cmap and clim (color range) changes
        self.param_stream = hv.streams.Params(self, ['cmap', 'clim'],
                                              rename={'cmap': 'cmap_val', 'clim': 'clim_val'})

        # Return a DynamicMap that updates when update_stream or range_stream is triggered
        # We also watch param_stream so the title (which shows the scale) updates
        self.dmap = hv.DynamicMap(self._render_plot, 
                                  streams=[self.update_stream, self.range_stream, self.param_stream])

        # Wrap in rasterize: it will render the data into an image server-side
        styled_dmap = rasterize(self.dmap, pixel_ratio=2).opts(
            colorbar=True,
            responsive=True,
            shared_axes=False,
            default_tools=[],
            tools=['hover','pan','wheel_zoom'],
            active_tools=['pan','wheel_zoom']
        )

        # Overlay with tiles
        tiles = gv.tile_sources.OSM()

        # Overlay with click marker
        marker_dmap = self._build_marker_overlay()
        final_plot = (tiles * styled_dmap * marker_dmap)

        return final_plot

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
        # Time controls from parent (specifying animate_coord)
        label = self.coord_names[0].capitalize() if len(self.coord_names) > 0 else "Slice"
        time_controls = self._make_nav_controls(
            self.first_slice, self.prev_slice, self.next_slice, self.last_slice,
            label=label,
            anim_coord=self.coord_names[0]
        )
        
        # Depth controls using helper from parent (specifying animate_coord)
        depth_label = self.coord_names[1].capitalize() if len(self.coord_names) > 1 else "Depth"
        depth_controls = self._make_nav_controls(
            self.first_depth, self.prev_depth, self.next_depth, self.last_depth,
            label=depth_label,
            anim_coord=self.coord_names[1]
        )
        
        return pn.Column(time_controls, depth_controls)

