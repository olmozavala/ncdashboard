import xarray as xr
from loguru import logger
from os.path import join
from model.AnimationNode import AnimationNode
from model.FourDNode import FourDNode
from model.OneDNode import OneDNode
from model.ProfileNode import ProfileNode
from model.ThreeDNode import ThreeDNode
from model.TwoDNode import TwoDNode
from model.FigureNode import FigureNode
import panel as pn
import holoviews as hv
from model.model_utils import PlotType, select_profile, select_spatial_location
from proj_layout.utils import select_colormap
from model import state as state_module

class Dashboard:
    def __init__(self, path, regex):
        self.path = path
        self.regex = regex

        logger.info(f"Opening files in {self.path} with regex {self.regex}")
        if isinstance(self.path, list):
            data = xr.open_mfdataset(self.path, decode_times=False)
        else:
            data = xr.open_mfdataset(join(self.path, self.regex), decode_times=False)

        self.tree_root = TwoDNode('root', data=data, parent=None)
        
        # Identify field dimensions
        self.four_d = []
        self.three_d = []
        self.two_d = []
        self.one_d = []
        
        for var in data.variables:
            shape_len = len(data[var].shape)
            if shape_len == 4:
                self.four_d.append(var)
                logger.info(f"Variable {var} added to 4D list")
            elif shape_len == 3:
                self.three_d.append(var)
                logger.info(f"Variable {var} added to 3D list")
            elif shape_len == 2:
                self.two_d.append(var)
                logger.info(f"Variable {var} added to 2D list")
            elif shape_len == 1:
                self.one_d.append(var)
                logger.info(f"Variable {var} added to 1D list")
        
        self.data = data

    def _cmap_from_name(self, name: str):
        """Resolve colormap name (cmocean or matplotlib) to object."""
        import cmocean
        cmo_names = ['thermal', 'haline', 'algae', 'matter', 'turbid', 'speed', 'amp', 'tempo', 'gray', 'balance', 'curl', 'diff', 'oxy', 'dense', 'ice', 'deep']
        if name in cmo_names:
            return getattr(cmocean.cm, name)
        return name

    def _apply_node_state(self, node, state: dict):
        """Apply saved state (cmap, cnorm, indices) to a node."""
        cmap_name = state.get("cmap")
        if cmap_name:
            node.cmap = self._cmap_from_name(cmap_name)
        cnorm = state.get("cnorm")
        if cnorm and hasattr(node, "cnorm"):
            node.cnorm = cnorm
        if hasattr(node, "third_coord_idx") and "third_coord_idx" in state:
            node.third_coord_idx = state["third_coord_idx"]
        if hasattr(node, "depth_idx") and "depth_idx" in state:
            node.depth_idx = state["depth_idx"]

    def get_state(self) -> dict:
        """Return full dashboard state for saving (path, regex, figures tree)."""
        return state_module.get_state_from_dashboard(self)

    def apply_state(self, state_dict: dict, layout_container) -> None:
        """
        Create figures from a saved state (path/regex must match current dashboard).
        Creates root-level figures first, then children (profiles, animations),
        applying cmap/cnorm/zoom/indices.
        """
        figures = state_dict.get("figures", [])
        
        # Sort figures so parents are created before children
        # We'll use a simple approach: first root, then others
        root_figures = [f for f in figures if f.get("parent_id") == "root"]
        child_figures = [f for f in figures if f.get("parent_id") != "root"]

        # Restore root figures
        for fig in root_figures:
            self._restore_figure(fig, layout_container)

        # Restore child figures (profiles, animations)
        # We might need multiple passes if there's deeper nesting, 
        # but currently it's mostly level 1 children.
        remaining = child_figures
        for _ in range(3): # max depth 3 for safety
            if not remaining: break
            still_remaining = []
            for fig in remaining:
                parent_id = fig.get("parent_id")
                parent_node = self.tree_root.locate(parent_id)
                if parent_node:
                    self._restore_figure(fig, layout_container, parent_node)
                else:
                    still_remaining.append(fig)
            remaining = still_remaining

    def _restore_figure(self, fig_state, layout_container, parent_node=None):
        """Helper to restore a single figure from its state."""
        pt_name = fig_state.get("plot_type", "TwoD")
        try:
            plot_type = getattr(PlotType, pt_name)
        except AttributeError:
            plot_type = PlotType.TwoD

        field_name = fig_state.get("field_name")
        node_id = fig_state.get("id")
        
        # For profiles, we need extra info
        if plot_type == PlotType.OneD and "lat" in fig_state and "lon" in fig_state:
            self.create_single_profile(
                fig_state["parent_id"], float(fig_state["lon"]), float(fig_state["lat"]),
                fig_state["dim_prof"], layout_container, state=fig_state
            )
            return

        # For animations, we need to create the AnimationNode
        if plot_type.is_animation():
            from model.AnimationNode import AnimationNode
            from model.model_utils import Resolutions
            
            anim_coord = fig_state.get("animation_coord")
            res_val = fig_state.get("spatial_res", Resolutions.HIGH.value)
            
            # Use provided parent or root
            effective_parent = parent_node or self.tree_root
            
            new_node = AnimationNode(
                node_id, self.data[field_name], anim_coord, res_val,
                field_name=field_name, parent=effective_parent,
                x_range=fig_state.get("x_range"), y_range=fig_state.get("y_range")
            )
            
            # Restore frame index if available
            if "frame_idx" in fig_state and hasattr(new_node, "player"):
                new_node.player.value = fig_state["frame_idx"]
                
            effective_parent.add_child(new_node)
            self.create_default_figure(None, plot_type, layout_container, new_node=new_node, state=fig_state)
            return

        # For default plots (2D, 3D, 4D)
        self.create_default_figure(field_name, plot_type, layout_container=layout_container, state=fig_state)
        
        # Restore viewport if applicable
        node = self.tree_root.locate(node_id)
        if node and hasattr(node, "range_stream") and node.range_stream is not None:
            xr, yr = fig_state.get("x_range"), fig_state.get("y_range")
            if xr is not None and yr is not None and len(xr) >= 2 and len(yr) >= 2:
                try:
                    node.range_stream.event(x_range=(float(xr[0]), float(xr[1])), 
                                            y_range=(float(yr[0]), float(yr[1])))
                except (TypeError, ValueError):
                    pass

    def create_single_profile(self, parent_id: str, lon: float, lat: float, dim_prof: str,
                              layout_container, state=None):
        '''
        Creates a single profile for (parent_id, lon, lat, dim_prof) and adds it to layout_container.
        Used when loading state so we restore exactly one profile per saved entry.
        '''
        parent_node = self.tree_root.locate(parent_id)
        if not parent_node:
            logger.warning(f"apply_state: parent node {parent_id} not found for profile")
            return
        data = parent_node.get_data()
        parent_node_id = parent_node.get_id()
        parent_field = parent_node.get_field_name()
        parent_coord_names = parent_node.get_coord_names()
        subset_data = select_spatial_location(data, lat, lon, parent_coord_names)
        dims = subset_data.dims
        if dim_prof not in dims:
            logger.warning(f"apply_state: dim_prof {dim_prof} not in dims {dims}")
            return
        id = state.get("id", self.id_generator(f"{parent_node_id}_{dim_prof}_prof")) if state else self.id_generator(f"{parent_node_id}_{dim_prof}_prof")
        title = f'{parent_node.get_long_name()} at {lat:0.2f}, {lon:0.2f} ({dim_prof.capitalize()})'
        profile_data = select_profile(subset_data, dim_prof, dims)
        new_node = ProfileNode(id, profile_data, lat, lon, dim_prof, title, plot_type=PlotType.OneD,
                              field_name=parent_field, parent=parent_node)
        parent_node.add_child(new_node)
        self.create_default_figure(None, PlotType.OneD, layout_container, new_node=new_node, state=state)

    def create_default_figure(self, c_field, plot_type, layout_container=None, new_node=None, state=None):
        '''
        Creates a figure for the dashboard. Returns a Panel object (Column).
        If state is provided (from load), uses state id/cmap/cnorm/indices and applies them.
        '''
        # Log plot creation details
        dims_str = "Unknown"
        if plot_type == PlotType.FourD: dims_str = "4D"
        elif plot_type == PlotType.ThreeD: dims_str = "3D"
        elif plot_type == PlotType.TwoD: dims_str = "2D"
        elif plot_type == PlotType.OneD: dims_str = "1D"
        # Get field name if not provided
        if c_field is None and new_node is not None:
            c_field = new_node.get_field_name()
        if state is not None and c_field is None:
            c_field = state.get("field_name")
            
        # Get data shape for logging
        shape_str = str(self.data[c_field].shape)
        logger.info(f"Creating new plot - Dimensions: {dims_str}, Field: {c_field}, Shape: {shape_str}")

        if new_node is None:
            id = state.get("id", self.id_generator(c_field)) if state else self.id_generator(c_field)
            third_coord_idx = state.get("third_coord_idx", 0) if state else 0
            time_idx = state.get("time_idx", 0) if state else 0
            depth_idx = state.get("depth_idx", 0) if state else 0

            if plot_type == PlotType.ThreeD:
                new_node = ThreeDNode(id, self.data[c_field], third_coord_idx=third_coord_idx,
                                        plot_type=plot_type, field_name=c_field, parent=self.tree_root)
            elif plot_type == PlotType.FourD:
                new_node = FourDNode(id, self.data[c_field], time_idx=time_idx, depth_idx=depth_idx, 
                                        plot_type=plot_type, field_name=c_field, parent=self.tree_root)
            elif plot_type == PlotType.OneD:
                new_node = OneDNode(id, self.data[c_field], plot_type=plot_type, field_name=c_field, 
                                        parent=self.tree_root)
            else: 
                new_node = TwoDNode(id, self.data[c_field], plot_type=plot_type, field_name=c_field, 
                                        parent=self.tree_root)

            self.tree_root.add_child(new_node)

        # Apply saved state (cmap, cnorm, indices) when loading
        if state is not None:
            self._apply_node_state(new_node, state) 

        # Create HoloViews object
        hv_obj = new_node.create_figure()
        
        # Setup Tap stream for 2D/3D/4D plots (Drill Down)
        if plot_type in [PlotType.TwoD, PlotType.ThreeD, PlotType.FourD, PlotType.ThreeD_Animation, PlotType.FourD_Animation]:
            stream_source = new_node.get_stream_source()
            tap = hv.streams.Tap(source=stream_source)
            
            def tap_callback(x, y):
                if x is None or y is None: 
                    return
                # Update marker list and stream
                new_node.clicked_points.append((x, y))
                new_node.marker_stream.event(x=x, y=y)
                # Show notification for feedback
                pn.state.notifications.success(f"Profile generated at {y:0.2f}, {x:0.2f}", duration=2000)
                # Create profile
                self.create_profiles(new_node.id, x, y, layout_container)
            
            tap.add_subscriber(tap_callback)

        # Create Panel container
        # We wrap in a Pane to ensure it renders correctly
        pane = pn.pane.HoloViews(hv_obj, sizing_mode='stretch_both', min_height=400)
        
        container = pn.Column(
            sizing_mode='fixed', # Allow FlexBox to wrap it
            width=600, # Approx half width of 1080p screen, or good size for 2-col
            min_height=480,
            margin=(10, 10),
            styles={'background': getattr(new_node, 'background_color', '#f0f0f0'), 'border-radius': '5px', 'padding': '10px'}
        )
        
        # Maximize/Restore Button
        # Toggle between fixed size and full screen (stretch both)
        # Using ⛶ (Square Four Corners) for maximize
        max_btn = pn.widgets.Button(name="⛶", button_type="light", width=40, height=30, align='center', margin=(0, 5, 0, 0))
        
        def toggle_size(event):
            if container.sizing_mode == 'fixed':
                # Maximizing
                container.sizing_mode = 'stretch_both'
                container.width = None
                container.height = None
                container.max_width = None
                
                container.styles.update({
                    'height': '85vh', 
                    'width': '95vw',
                    'z-index': '1000',
                    'position': 'relative'
                })
                
                container.margin = (5, 5)
                max_btn.name = "🗗" # Symbol for restore
                new_node.maximized = True
            else:
                # Restoring
                container.styles.update({
                    'height': 'auto',
                    'width': '600px',
                    'z-index': '1',
                    'position': 'static'
                })

                container.sizing_mode = 'fixed'
                container.width = 600
                container.max_width = 600
                container.height = None
                container.min_height = 480
                
                container.margin = (10, 10)
                max_btn.name = "⛶" # Symbol for maximize
                new_node.maximized = False
            
            # Trigger re-render/re-rasterization of the figure
            pane.param.trigger('object')
            container.param.trigger('styles')
            container.param.trigger('sizing_mode')
        
        max_btn.on_click(toggle_size)

        # Check for initial maximized state from saved state
        if (state and state.get('maximized')) or getattr(new_node, 'maximized', False):
             toggle_size(None)

        # --- UI Controls for the Plot ---
        import cmocean
        cmo_names = ['thermal', 'haline', 'algae', 'matter', 'turbid', 'speed', 'amp', 'tempo', 'gray', 'balance', 'curl', 'diff', 'oxy', 'dense', 'ice', 'deep']
        cmap_options = cmo_names + ['viridis', 'inferno', 'plasma', 'magma', 'rainbow', 'jet', 'coolwarm']
        
        # Determine initial colormap
        initial_cmap = 'viridis' 
        if hasattr(new_node.cmap, 'name'):
            name = new_node.cmap.name.split('.')[-1]
            if name in cmap_options:
                initial_cmap = name

        # Colormap Select
        cmap_select = pn.widgets.Select(
            name="", options=cmap_options, value=initial_cmap,
            width=120, height=30, align='center', margin=(0, 10)
        )

        def update_plot_view(event):
            # Update Node parameters - This triggers the reactive HoloViews pipeline
            # without replacing the pane.object, thus preserving zoom/pan perfectly.
            if event.obj == cmap_select:
                new_val = event.new
                new_cmap = getattr(cmocean.cm, new_val) if new_val in cmo_names else new_val
                new_node.cmap = new_cmap

            # Clear cache for animations
            if hasattr(new_node, '_cache'):
                new_node._cache.clear()

            # For animations, we still trigger the UI sync
            if hasattr(new_node, 'player'):
                new_node.player.param.trigger('value')

        cmap_select.param.watch(update_plot_view, 'value')

        # Header with Controls
        close_btn = pn.widgets.Button(name="x", button_type="danger", width=30, height=30, align='center')
        header_row = pn.Row(
            pn.pane.Markdown("**Cmap:**", align='center', margin=(0, 0, 0, 5)),
            cmap_select,
            pn.layout.HSpacer(),
            max_btn,
            close_btn
        )
        
        def close_action(event):
            if layout_container is not None:
                # Remove self from layout
                try:
                    layout_container.remove(container)
                except ValueError:
                    pass # Already removed
            else:
                container.visible = False
            
            # Remove from tree
            self.tree_root.remove_id(new_node.id) 

        close_btn.on_click(close_action)
        
        # Navigation Buttons for 3D/4D
        # Navigation Buttons (Delegated to Node)
        nav_row = new_node.get_controls()

        container.extend([header_row, pane])
        if nav_row:
             container.append(nav_row)

        # Store view container in node so it can replace itself (e.g. for animation)
        new_node.view_container = container
        new_node.id_generator_callback = self.id_generator
        
        # Add to layout if provided
        if layout_container is not None:
             layout_container.append(container)
        
        # Callback to add new node (e.g. animation) to the dashboard
        def add_node_cb(added_node):
             if added_node not in new_node.get_children():
                  added_node.id_generator_callback = self.id_generator
                  new_node.add_child(added_node)
             
             # Create figure pane (recursively adds to layout_container)
             # layout_container is captured from closure
             self.create_default_figure(None, added_node.get_plot_type(), layout_container=layout_container, new_node=added_node)
             
        new_node.add_node_callback = add_node_cb
        
        return container

    def close_figure(self, node_id, prev_children, patch):
        """Removes a node from the tree and generates a Dash patch to remove it from UI."""
        logger.info(f"Closing figure: {node_id}")
        
        # Remove from tree
        self.tree_root.remove_id(node_id)
        
        # Find index in prev_children for Dash patch
        for idx, child in enumerate(prev_children):
            # Dash IDs are often formatted like "type:index"
            comp_id = child['props']['id']
            if isinstance(comp_id, str) and node_id in comp_id:
                del patch[idx]
                break
            elif isinstance(comp_id, dict) and comp_id.get('index') == node_id:
                del patch[idx]
                break
                
        return patch

    def create_profiles(self, parent_id, lon, lat, layout_container):
        '''
        Creates a profile for the given parent_id and triggered coordinates (lon, lat).
        Adds the result to layout_container.
        '''
        parent_node = self.tree_root.locate(parent_id)
        if not parent_node:
            return

        data = parent_node.get_data()
        parent_node_id = parent_node.get_id()
        parent_field = parent_node.get_field_name()
        parent_coord_names = parent_node.get_coord_names()

        # Select spatial location
        subset_data = select_spatial_location(data, lat, lon, parent_coord_names)
        dims = subset_data.dims

        for c_dim in dims:
            id = self.id_generator(f'{parent_node_id}_{c_dim}_prof')
            title = f'{parent_node.get_long_name()} at {lat:0.2f}, {lon:0.2f} ({c_dim.capitalize()})'

            profile_data = select_profile(subset_data, c_dim, dims)
            
            new_node = ProfileNode(id, profile_data, lat, lon, c_dim, title, plot_type=PlotType.OneD, 
                                field_name=parent_field, parent=parent_node)

            parent_node.add_child(new_node) 
            
            # create_default_figure appends to layout_container automatically
            self.create_default_figure(None, PlotType.OneD, layout_container, new_node=new_node)

    def get_field_names(self, var_type):
        dim_fields = []
        if var_type == "1D": dim_fields = self.one_d
        elif var_type == "2D": dim_fields = self.two_d
        elif var_type == "3D": dim_fields = self.three_d
        elif var_type == "4D": dim_fields = self.four_d
        
        results = []
        for f in dim_fields:
            if hasattr(self.data[f], 'long_name'):
                name = self.data[f].long_name
            else:
                name = f
            results.append((name, f, str(self.data[f].shape)))
            
        return results

    def id_generator(self, field_name):
        new_id = field_name
        count = 2
        while self.tree_root.locate(new_id) is not None:
            new_id = field_name + f'_{count}'
            count += 1
        return new_id
    
    def create_figure_from_dataarray(
        self,
        data: xr.DataArray,
        parent_node,
        title: str,
        layout_container
    ):
        """
        Create an appropriate figure from an xarray DataArray.
        
        Determines the node type based on data dimensionality and creates
        the corresponding visualization.
        
        Args:
            data: xarray DataArray to visualize
            parent_node: Parent node for the new figure
            title: Title for the figure
            layout_container: Panel container to add the figure to
        """
        from loguru import logger
        
        # Determine dimensionality
        ndims = len(data.dims)
        logger.info(f"Creating figure from DataArray: dims={data.dims}, shape={data.shape}")
        
        # Generate unique ID
        base_id = f"llm_{title[:20].replace(' ', '_').lower()}"
        node_id = self.id_generator(base_id)
        
        # Get or set field name
        field_name = data.name or "llm_output"
        
        # Ensure the data has a name attribute  
        if data.name is None:
            data.name = field_name
        
        # Create appropriate node type based on dimensions
        if ndims == 1:
            plot_type = PlotType.OneD
            new_node = OneDNode(
                node_id, 
                data, 
                title=title,
                field_name=field_name,
                plot_type=plot_type,
                parent=parent_node
            )
        elif ndims == 2:
            plot_type = PlotType.TwoD
            new_node = TwoDNode(
                node_id,
                data,
                title=title,
                field_name=field_name,
                plot_type=plot_type,
                parent=parent_node
            )
        elif ndims == 3:
            plot_type = PlotType.ThreeD
            new_node = ThreeDNode(
                node_id,
                data,
                title=title,
                field_name=field_name,
                plot_type=plot_type,
                parent=parent_node,
                third_coord_idx=0
            )
        else:  # 4D or more
            plot_type = PlotType.FourD
            new_node = FourDNode(
                node_id,
                data,
                title=title,
                field_name=field_name,
                plot_type=plot_type,
                parent=parent_node,
                time_idx=0,
                depth_idx=0
            )
        
        # Add to parent
        parent_node.add_child(new_node)
        
        # Create the figure UI
        self.create_default_figure(
            None, 
            plot_type, 
            layout_container=layout_container, 
            new_node=new_node
        )
        
        logger.info(f"Created LLM figure: id={node_id}, type={plot_type.name}")
        return new_node