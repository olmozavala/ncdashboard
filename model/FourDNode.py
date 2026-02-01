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

        if self.plot_type == PlotType.FourD:
            # We use self.third_coord_idx (from parent) for the first dimension (Time)
            current_slice = data[self.third_coord_idx, self.depth_idx,:,:]

        title = f'{self.title} ({self.cnorm}) at {self.coord_names[0].capitalize()} {self.third_coord_idx} and {self.coord_names[1].capitalize()} {self.depth_idx}'
        
        # Use geoviews Image for geographic plotting
        img = gv.Image((lons, lats, current_slice.values), [self.coord_names[-1], self.coord_names[-2]], crs=ccrs.PlateCarree())
        return img.opts(title=title, cmap=colormap, cnorm=self.cnorm)

    def create_figure(self):
        # Create a stream that watches for cmap and cnorm changes
        self.param_stream = hv.streams.Params(self, ['cnorm', 'cmap'])

        # Return a DynamicMap that updates when update_stream or range_stream is triggered
        # We also watch param_stream so the title (which shows the scale) updates
        self.dmap = hv.DynamicMap(self._render_plot, 
                                  streams=[self.update_stream, self.range_stream, self.param_stream])
        
        # Apply rasterization to the DynamicMap
        rasterized = rasterize(self.dmap, width=800).apply.opts(
            cmap=self.param.cmap,
            cnorm=self.cnorm,
            tools=['hover', 'save', 'copy'],
            colorbar=True,
            responsive=True,
            aspect='equal'
        )
        
        # Link range stream for viewport tracking
        self.range_stream.source = rasterized

        # Overlay with tiles
        tiles = gv.tile_sources.OSM()
        return (tiles * rasterized).opts(
            active_tools=['wheel_zoom', 'pan'],
            default_tools=['pan', 'wheel_zoom', 'save', 'copy', 'reset']
        )

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
    
    def _create_transect(self):
        """
        Override transect creation for 4D data.
        Creates spatial transect (lat/lon) preserving time and depth dimensions.
        Output is a ThreeDNode with time slider (distance × depth, navigable by time).
        """
        if self.transect_stream is None or not self.transect_stream.data:
            logger.warning("No transect path drawn yet")
            return
            
        xs_list = self.transect_stream.data.get('xs', [])
        ys_list = self.transect_stream.data.get('ys', [])
        
        if not xs_list or len(xs_list[0]) < 2:
            logger.warning("Transect path must have at least 2 points")
            return
            
        path_xs = xs_list[0]
        path_ys = ys_list[0]
        
        logger.info(f"Creating spatial transect with {len(path_xs)} vertices from 4D data")
        
        if self.add_node_callback is None:
            logger.warning("No add_node_callback found for transect creation")
            return
            
        from model.transect_utils import extract_transect, get_transect_title
        
        # Extract transect data (4D -> 3D: time × depth × distance)
        transect_data = extract_transect(self.data, path_xs, path_ys)
        
        # Generate title
        start_point = (path_xs[0], path_ys[0])
        end_point = (path_xs[-1], path_ys[-1])
        title = get_transect_title(self.title, start_point, end_point)
        
        # Create ThreeDNode for 3D transect output
        # The output has dims: [time, depth, distance]
        # We'll display it as distance × depth with time navigation
        new_node = ThreeDNode(
            id=f"{self.id}_transect",
            data=transect_data,
            third_coord_idx=0,
            title=title,
            field_name=self.field_name,
            plot_type=PlotType.Transect_3D,
            parent=self
        )
        
        self.add_node_callback(new_node)
        logger.info(f"Created transect node: {new_node.id}")

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

