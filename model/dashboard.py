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
            tap = hv.streams.Tap(source=hv_obj)
            
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
        
        # Close Button
        header_row = pn.Row(
            pn.layout.HSpacer(),
            pn.widgets.Button(name="x", button_type="danger", width=30, height=30, align='center')
        )
        close_btn = header_row[1]
        
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
            
            # Create the figure container using create_default_figure logic re-used or manual?
            # Re-using create_default_figure allows recursive close logic
            fig_container = self.create_default_figure(None, PlotType.OneD, layout_container, new_node=new_node)
            
            if layout_container is not None:
                layout_container.append(fig_container)

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