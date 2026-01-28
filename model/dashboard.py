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

    def create_default_figure(self, c_field, plot_type, layout_container=None, new_node=None):
        '''
        Creates a figure for the dashboard. Returns a Panel object (Column).
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
            
        # Get data shape for logging
        shape_str = str(self.data[c_field].shape)
        logger.info(f"Creating new plot - Dimensions: {dims_str}, Field: {c_field}, Shape: {shape_str}")

        if new_node is None:
            id = self.id_generator(c_field)

            if plot_type == PlotType.ThreeD:
                new_node = ThreeDNode(id, self.data[c_field], third_coord_idx=0,
                                        plot_type=plot_type, field_name=c_field, parent=self.tree_root)
            elif plot_type == PlotType.FourD:
                new_node = FourDNode(id, self.data[c_field], time_idx=0, depth_idx=0, 
                                        plot_type=plot_type, field_name=c_field, parent=self.tree_root)
            elif plot_type == PlotType.OneD:
                new_node = OneDNode(id, self.data[c_field], plot_type=plot_type, field_name=c_field, 
                                        parent=self.tree_root)
            else: 
                new_node = TwoDNode(id, self.data[c_field], plot_type=plot_type, field_name=c_field, 
                                        parent=self.tree_root)

            self.tree_root.add_child(new_node) 

        # Create HoloViews object
        hv_obj = new_node.create_figure()
        
        # Setup Tap stream for 2D/3D/4D plots (Drill Down)
        if plot_type in [PlotType.TwoD, PlotType.ThreeD, PlotType.FourD, PlotType.ThreeD_Animation, PlotType.FourD_Animation]:
            stream_source = new_node.get_stream_source()
            tap = hv.streams.Tap(source=stream_source)
            
            def tap_callback(x, y):
                if x is None or y is None: 
                    return
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
            styles={'background': '#f0f0f0', 'border-radius': '5px', 'padding': '10px'}
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
            
            # Trigger re-render/re-rasterization of the figure
            pane.param.trigger('object')
            container.param.trigger('styles')
            container.param.trigger('sizing_mode')
        
        max_btn.on_click(toggle_size)

        # Close Button
        header_row = pn.Row(
            pn.layout.HSpacer(),
            max_btn,
            pn.widgets.Button(name="x", button_type="danger", width=30, height=30, align='center')
        )
        close_btn = header_row[2]
        
        def close_action(event):
            if layout_container is not None:
                # Remove self from layout
                try:
                    layout_container.remove(container)
                except ValueError:
                    pass # Already removed
            else:
                container.visible = False
            
            # Remove from tree?
            # self.tree_root.remove_id(new_node.id) 

        close_btn.on_click(close_action)
        
        # Navigation Buttons for 3D/4D
        # Navigation Buttons (Delegated to Node)
        nav_row = new_node.get_controls()

        container.extend([header_row, pane])
        if nav_row:
             container.append(nav_row)

        # Store view container in node so it can replace itself (e.g. for animation)
        new_node.view_container = container
        
        # Add to layout if provided
        if layout_container is not None:
             layout_container.append(container)
        
        # Callback to add new node (e.g. animation) to the dashboard
        def add_node_cb(added_node):
             if added_node not in new_node.get_children():
                  new_node.add_child(added_node)
             
             # Create figure pane (recursively adds to layout_container)
             # layout_container is captured from closure
             self.create_default_figure(None, added_node.get_plot_type(), layout_container=layout_container, new_node=added_node)
             
        new_node.add_node_callback = add_node_cb
        
        return container

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