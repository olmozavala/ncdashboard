import holoviews as hv
import geoviews as gv
import panel as pn
import cartopy.crs as ccrs
from holoviews.operation.datashader import rasterize
from holoviews import streams
from loguru import logger

from model.FigureNode import FigureNode
from model.AnimationNode import AnimationNode
from model.model_utils import PlotType, Resolutions, get_all_coords

class ThreeDNode(FigureNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st dimensions may not be time, we are still calling it like that. 
    def __init__(self, id, data, third_coord_idx=0, plot_type=PlotType.ThreeD, 
                 title=None, field_name=None, bbox=None, parent=None, cmap=None, **params):

        super().__init__(id, data, title=title, field_name=field_name, 
                         bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap, **params)

        self.third_coord_idx = third_coord_idx
        logger.info(f"Created ThreeDNode: id={id}, shape={data.shape}, coords={self.coord_names}")
        self.third_coord_name = data.coords[self.coord_names[0]].name
        
        # Stream for dynamic updates
        self.update_stream = hv.streams.Counter()
        # Stream for capturing viewport ranges (for animation)
        self.range_stream = hv.streams.RangeXY()
        
        # Transect mode state
        self.transect_mode = False
        self.transect_path = None
        self.transect_stream = None

    def _render_plot(self, counter=0, **kwargs):
        colormap = self.cmap
        
        data = self.data
        if self.plot_type == PlotType.ThreeD:
            # We assume logical structure [time, lat, lon] for 3D
            # Select the time slice
            data = self.data[self.third_coord_idx, :, :]

        # We assume the last two coordinates are spatial (lat, lon)
        lats = data.coords[self.coord_names[-2]].values
        lons = data.coords[self.coord_names[-1]].values

        title = f'{self.title} ({self.cnorm}) at {self.coord_names[0].capitalize()} {self.third_coord_idx}'

        # Use geoviews Image for geographic plotting
        img = gv.Image((lons, lats, data.values), [self.coord_names[-1], self.coord_names[-2]], crs=ccrs.PlateCarree())
        return img.opts(title=title, cmap=colormap, cnorm=self.cnorm, clim=self.clim)

    def create_figure(self):
        # Create a stream that watches for cmap, cnorm and clim changes
        self.param_stream = hv.streams.Params(self, ['cnorm', 'cmap', 'clim'])

        # Return a DynamicMap that updates when update_stream or range_stream is triggered
        # We also watch param_stream so the title (which shows the scale) updates
        self.dmap = hv.DynamicMap(self._render_plot, 
                                  streams=[self.update_stream, self.range_stream, self.param_stream])
        
        # Apply rasterization to the DynamicMap
        # We use .apply.opts to link cmap and clim to the parameter reactively
        rasterized = rasterize(self.dmap, width=800).apply.opts(
            cmap=self.param.cmap,
            clim=self.param.clim,
            tools=['hover', 'save', 'copy'],
            colorbar=True,
            responsive=True,
            aspect='equal'
        )
        
        # Link range stream for viewport tracking
        self.range_stream.source = rasterized

        # Overlay with tiles
        tiles = gv.tile_sources.OSM()
        base_plot = (tiles * rasterized).opts(
            active_tools=['wheel_zoom', 'pan'],
            default_tools=['pan', 'wheel_zoom', 'save', 'copy', 'reset']
        )

        # Overlay with click marker
        def _get_marker(x, y):
            kdims = [self.coord_names[-1], self.coord_names[-2]]
            
            # Previous points in yellow
            prev_points = self.clicked_points[:-1]
            # Latest point in red to show "it has just clicked"
            latest_point = self.clicked_points[-1:]
            
            p_prev = gv.Points(prev_points, kdims=kdims, crs=ccrs.PlateCarree()).opts(
                color='yellow', size=12, marker='star', line_color='black', line_width=1
            )
            p_latest = gv.Points(latest_point, kdims=kdims, crs=ccrs.PlateCarree()).opts(
                color='red', size=15, marker='star', line_color='black', line_width=1
            )
            return p_prev * p_latest
            
        marker_dmap = gv.project(hv.DynamicMap(_get_marker, streams=[self.marker_stream]), projection=ccrs.GOOGLE_MERCATOR)
        return base_plot * marker_dmap

    def get_stream_source(self):
        if not hasattr(self, 'dmap'):
            self.create_figure()
        return self.dmap

    def next_slice(self):
        self.third_coord_idx = (self.third_coord_idx + 1) % len(self.data[self.coord_names[0]])
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.third_coord_idx
    
    def prev_slice(self):
        self.third_coord_idx = (self.third_coord_idx - 1) % len(self.data[self.coord_names[0]])
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.third_coord_idx

    def set_third_coord_idx(self, third_coord_idx):
        self.third_coord_idx = third_coord_idx
        self.update_stream.event(counter=self.update_stream.counter + 1)
        
    def get_third_coord_idx(self):
        return self.third_coord_idx

    def first_slice(self):
        self.third_coord_idx = 0
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.third_coord_idx

    def last_slice(self):
        self.third_coord_idx = len(self.data[self.coord_names[0]]) - 1
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.third_coord_idx

    def _animate_callback(self, animation_coord, data=None):
        """
        Creates an AnimationNode and adds it to the dashboard via callback.
        """
        if self.add_node_callback is None:
            logger.warning("No add_node_callback found for animation callback")
            return

        x_range = self.range_stream.x_range
        y_range = self.range_stream.y_range
        
        logger.info(f"Starting animation for {animation_coord} in range X:{x_range} Y:{y_range}")

        # Use provided data or default to self.data
        data_to_use = data if data is not None else self.data

        # Use callback if available to generate unique ID
        if self.id_generator_callback:
            node_id = self.id_generator_callback(f"{self.id}_anim")
        else:
            node_id = f"{self.id}_anim"

        # Create Animation Node (High Resolution, PlateCarree)
        # Using self as parent allows the animation node to be aware of its origin
        anim_node = AnimationNode(node_id, data_to_use, animation_coord, Resolutions.HIGH.value, 
                                  title=self.title, field_name=self.field_name, 
                                  bbox=self.bbox, parent=self, cmap=self.cmap,
                                  x_range=x_range, y_range=y_range)
        
        # Trigger callback to add node to layout
        self.add_node_callback(anim_node)
    
    def _init_transect_mode(self):
        """Initialize transect drawing mode with PolyDraw stream."""
        if self.transect_stream is not None:
            return  # Already initialized
            
        # Create an empty Path for drawing transects
        self.transect_path = gv.Path([], crs=ccrs.PlateCarree()).opts(
            color='red', 
            line_width=3,
            tools=['poly_draw']
        )
        
        # Create PolyDraw stream linked to the path
        self.transect_stream = streams.PolyDraw(
            source=self.transect_path,
            drag=True,
            num_objects=1,
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
            
        xs_list = self.transect_stream.data.get('xs', [])
        ys_list = self.transect_stream.data.get('ys', [])
        
        if not xs_list or len(xs_list[0]) < 2:
            logger.warning("Transect path must have at least 2 points")
            return
            
        path_xs = xs_list[0]
        path_ys = ys_list[0]
        
        logger.info(f"Creating transect with {len(path_xs)} vertices from 3D data")
        
        if self.add_node_callback is None:
            logger.warning("No add_node_callback found for transect creation")
            return
            
        from model.transect_utils import extract_transect, get_transect_title
        from model.TwoDNode import TwoDNode
        
        # Extract transect data (3D -> 2D: distance × 3rd coord)
        transect_data = extract_transect(self.data, path_xs, path_ys)
        
        # Generate title
        start_point = (path_xs[0], path_ys[0])
        end_point = (path_xs[-1], path_ys[-1])
        title = get_transect_title(self.title, start_point, end_point)
        
        # Create TwoDNode for 2D transect output (non-geographic)
        # Note: This will show distance × third_coord as a heatmap
        new_node = TwoDNode(
            id=f"{self.id}_transect",
            data=transect_data,
            title=title,
            field_name=self.field_name,
            plot_type=PlotType.Transect_2D,
            parent=self
        )
        
        self.add_node_callback(new_node)
        logger.info(f"Created transect node: {new_node.id}")

    def _make_nav_controls(self, first_cb, prev_cb, next_cb, last_cb, label=None, anim_coord=None):
        btn_style = {'margin': '0px 2px'}
        btn_first = pn.widgets.Button(name="\u00ab", icon="angles-left", width=40, height=30, styles=btn_style)
        btn_prev = pn.widgets.Button(name="\u2039", icon="angle-left", width=40, height=30, styles=btn_style)
        btn_next = pn.widgets.Button(name="\u203a", icon="angle-right", width=40, height=30, styles=btn_style)
        btn_last = pn.widgets.Button(name="\u00bb", icon="angles-right", width=40, height=30, styles=btn_style)
        
        # Animation Button
        btn_anim = pn.widgets.Button(name="Animate", icon="film", button_type="primary", height=30, styles=btn_style)

        btn_first.on_click(lambda e: first_cb())
        btn_prev.on_click(lambda e: prev_cb())
        btn_next.on_click(lambda e: next_cb())
        btn_last.on_click(lambda e: last_cb())
        
        if anim_coord:
            btn_anim.on_click(lambda e: self._animate_callback(anim_coord))
        else:
             btn_anim.disabled = True
        
        row_content = [pn.layout.HSpacer()]
        if label:
            row_content.append(pn.pane.Markdown(f"**{label}:**", align='center', margin=(0, 10)))
        
        # Add navigation and animation buttons to the row
        row_content.extend([btn_first, btn_prev, btn_next, btn_last, btn_anim, pn.layout.HSpacer()])
        
        return pn.Row(*row_content, align='center')

    def get_controls(self):
        label = self.coord_names[0].capitalize() if len(self.coord_names) > 0 else "Slice"
        return self._make_nav_controls(
            self.first_slice, self.prev_slice, self.next_slice, self.last_slice,
            label=label,
            anim_coord=self.coord_names[0]
        )
