
import holoviews as hv
import geoviews as gv
import panel as pn
import cartopy.crs as ccrs
from holoviews.operation.datashader import rasterize
from holoviews import streams

from model.FigureNode import FigureNode
from model.model_utils import PlotType
from loguru import logger

class TwoDNode(FigureNode):
    def __init__(self, id, data, title=None, field_name=None, bbox=None, 
                 plot_type=PlotType.TwoD, parent=None, cmap=None, **params):
        super().__init__(id, data, title=title, field_name=field_name,
                         bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap, **params)
        shape_str = str(data.shape) if hasattr(data, 'shape') else "Dataset (no shape)"
        logger.info(f"Created TwoDNode: id={id}, shape={shape_str}, coords={self.coord_names}")
        
        # Transect mode state
        self.transect_mode = False
        self.transect_path = None
        self.transect_stream = None

    def create_figure(self):
        # Assume 2D data: [lat, lon] or [y, x]
        lats = self.data.coords[self.coord_names[-2]].values
        lons = self.data.coords[self.coord_names[-1]].values

        # Use geoviews Image for geographic plotting
        vdims = [hv.Dimension(self.field_name, label=self.label)]
        self.img = gv.Image((lons, lats, self.data), [self.coord_names[-1], self.coord_names[-2]], 
                            vdims=vdims, crs=ccrs.PlateCarree())

        # We wrap in a DynamicMap to allow reactive updates to cmap 
        # without replacing the entire figure object in the UI.
        def _get_image(cmap, clim):
            return self.img.opts(cmap=cmap, clim=clim)
        
        # Create stream for cmap and clim (color range)
        self.param_stream = hv.streams.Params(self, ['cmap', 'clim'])
        self.dmap = hv.DynamicMap(_get_image, streams=[self.param_stream])

        # Project to Web Mercator BEFORE rasterizing for best performance/quality
        projected = gv.project(self.dmap, projection=ccrs.GOOGLE_MERCATOR)
        rasterized = rasterize(projected, pixel_ratio=2).opts(
            colorbar=True,
            responsive=True,
            shared_axes=False,
        )

        # Add tiles
        tiles = gv.tile_sources.OSM()

        self.base_plot = (tiles * rasterized).opts(
            tools=self.GEO_TOOLS,
            active_tools=self.GEO_ACTIVE_TOOLS,
            responsive=True,
            shared_axes=False
        )
        
        # Overlay with click marker
        marker_dmap = self._build_marker_overlay()
        # Apply hook on the FINAL overlay so it isn't lost
        self.base_plot = (self.base_plot * marker_dmap).opts(hooks=[self._activate_wheel_zoom])
        
        return self.base_plot

    def get_stream_source(self):
        if not hasattr(self, 'dmap'):
            self.create_figure()
        return self.dmap
    
    def _init_transect_mode(self):
        """Initialize transect drawing mode with PolyDraw stream."""
        if self.transect_stream is not None:
            return  # Already initialized
            
        # Create an empty Path for drawing transects
        # Using PlateCarree coordinates since that's our data CRS
        self.transect_path = gv.Path([], crs=ccrs.PlateCarree()).opts(
            color='red', 
            line_width=3,
            tools=['poly_draw']
        )
        
        # Create PolyDraw stream linked to the path
        self.transect_stream = streams.PolyDraw(
            source=self.transect_path,
            drag=True,
            num_objects=1,  # Only allow one transect at a time
            show_vertices=True,
            vertex_style={'fill_color': 'yellow', 'size': 8}
        )
        
        logger.info(f"Transect mode initialized for node {self.id}")
    
    def _toggle_transect_mode(self):
        """Toggle transect drawing mode on/off."""
        self.transect_mode = not self.transect_mode
        
        if self.transect_mode:
            self._init_transect_mode()
            logger.info(f"Transect mode ENABLED for node {self.id}")
        else:
            logger.info(f"Transect mode DISABLED for node {self.id}")
    
    def _create_transect(self):
        """Extract transect data and create output node."""
        if self.transect_stream is None or not self.transect_stream.data:
            logger.warning("No transect path drawn yet")
            return
            
        # Get path coordinates from stream
        xs_list = self.transect_stream.data.get('xs', [])
        ys_list = self.transect_stream.data.get('ys', [])
        
        if not xs_list or len(xs_list[0]) < 2:
            logger.warning("Transect path must have at least 2 points")
            return
            
        path_xs = xs_list[0]  # First (and only) path
        path_ys = ys_list[0]
        
        logger.info(f"Creating transect with {len(path_xs)} vertices")
        
        if self.add_node_callback is None:
            logger.warning("No add_node_callback found for transect creation")
            return
            
        # Import here to avoid circular imports
        from model.transect_utils import extract_transect, get_transect_title
        from model.OneDNode import OneDNode
        
        # Extract transect data
        transect_data = extract_transect(self.data, path_xs, path_ys)
        
        # Generate title
        start_point = (path_xs[0], path_ys[0])
        end_point = (path_xs[-1], path_ys[-1])
        title = get_transect_title(self.title, start_point, end_point)
        
        # Use callback if available to generate unique ID
        if self.id_generator_callback:
            node_id = self.id_generator_callback(f"{self.id}_transect")
        else:
            node_id = f"{self.id}_transect"

        # Create OneDNode for 1D transect output
        new_node = OneDNode(
            id=node_id,
            data=transect_data,
            title=title,
            field_name=self.field_name,
            plot_type=PlotType.Transect_1D,
            parent=self
        )
        
        # Trigger callback to add node to layout
        self.add_node_callback(new_node)
        
        logger.info(f"Created transect node: {new_node.id}")
    
    def get_controls(self):
        """Return control widgets for the node."""
        return None

    def get_figure_with_transect(self):
        """Return the figure with transect path overlay when in transect mode."""
        if self.transect_mode and self.transect_path is not None:
            return self.base_plot * self.transect_path
        return self.base_plot
