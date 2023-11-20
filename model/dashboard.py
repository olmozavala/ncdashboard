import xarray as xr
import logging
from os.path import join
from model.AnimationNode import AnimationNode
from model.FourDNode import FourDNode
from model.OneDNode import OneDNode
from model.ProfileNode import ProfileNode
from model.ThreeDNode import ThreeDNode
from model.TreeNode import FigureNode
import dash_bootstrap_components as dbc
from dash import Patch, html, dcc
from model.model_utils import PlotType, select_profile, select_spatial_location

from proj_layout.utils import get_buttons_config, get_def_slider, get_update_buttons, select_colormap

logger = logging.getLogger(__name__)

# Make a class with attributes and methods to create a dashboard

class Dashboard:
    def __init__(self, path, regex):
        self.path = path
        self.regex = regex

        logger.info(f"Opening files in {self.path} with regex {self.regex}")
        if isinstance(self.path, list):
            data = xr.open_mfdataset(self.path, decode_times=False)
        else:
            data = xr.open_mfdataset(join(self.path, self.regex), decode_times=False)

        self.tree_root = FigureNode('root', data=data, parent=None) # type: ignore
        # From data identify which fields are 3D, 2D and 1D
        four_d = []
        three_d = []
        two_d = []
        one_d = []
        for var in data.variables:
            if len(data[var].shape) == 4:
                four_d.append(var)
            if len(data[var].shape) == 3:
                three_d.append(var)
            elif len(data[var].shape) == 2:
                two_d.append(var)
            elif len(data[var].shape) == 1:
                one_d.append(var)
        
        self.data = data
        self.four_d = four_d
        self.three_d = three_d
        self.two_d = two_d
        self.one_d = one_d

    def create_default_figure(self, c_field, plot_type, new_node=None, window_ratio = 0.8):
        '''
        This method creates a default figure for the dashboard. It is called when the user hits the 'plot' button. 
        '''

        col_width = 4

        if new_node is None:
            id = self.id_generator(c_field)

            if plot_type == PlotType.ThreeD:
                new_node = ThreeDNode(id, self.data[c_field], time_idx=0,
                                        plot_type=plot_type, field_name=c_field, parent=self.tree_root) # type: ignore

            elif plot_type == PlotType.FourD:
                new_node = FourDNode(id, self.data[c_field], time_idx=0, depth_idx=0, 
                                        plot_type=plot_type, field_name=c_field, 
                                        parent=self.tree_root) # type: ignore

            elif plot_type == PlotType.OneD:
                new_node = OneDNode(id, self.data[c_field], plot_type=plot_type, field_name=c_field, 
                                        parent=self.tree_root) # type: ignore
            else: 
                new_node = FigureNode(id, self.data[c_field], plot_type=plot_type, field_name=c_field, 
                                        parent=self.tree_root) # type: ignore

            self.tree_root.add_child(new_node) # type: ignore

        fig = new_node.create_figure()
        plot_type = new_node.get_plot_type()
        
        coords = new_node.get_animation_coords()
        # If we have animation coords and we are not plotting an animation we make the buttons
        anim_options = []
        frame_controls = []
        if len(coords) > 0 and not plot_type.is_animation():
            anim_options = [
                dbc.Row( 
                    [
                        dbc.Col( html.Div("Resolution:"), width=3),
                        dbc.Col( dbc.RadioItems(
                                    id={"type": "resolution",
                                        "index": new_node.id},
                                    options=[
                                        {"label": "High", "value": f"{new_node.id}:high"},
                                        {"label": "Medium", "value": f"{new_node.id}:medium"},
                                        {"label": "Low", "value": f"{new_node.id}:low"},
                                    ],
                                    value=f"{new_node.id}:low",
                                    inline=True,
                                ),
                            width=9),
                    ]
                ),
                dbc.Row(
                    dbc.Col(
                            [ dbc.Button(f'Animate {anim_coord}', 
                                        id={"type": "animation", 
                                            "index": f'{new_node.id}:{anim_coord}'},
                                        size="sm",
                                        className="me-1",
                                        color='light'
                                        ) 
                                        for anim_coord in coords ],
                        width={'size':8, 'offset':2},
                        )
                    ),
            ]

            frame_controls = [
                # Add a div with the name of the field
                html.Div([f"{anim_coord}", 
                    dbc.ButtonGroup(
                    [
                        dbc.Button(html.I(className="bi bi-skip-backward"), color="light", id={"type":"first_frame", "index":f'{anim_coord}:{new_node.id}'}),
                        dbc.Button(html.I(className="bi bi-skip-start"),    color="light", id={"type":"prev_frame",  "index":f'{anim_coord}:{new_node.id}'}),
                        dbc.Button(html.I(className="bi bi-skip-end"),      color="light", id={"type":"next_frame",  "index":f'{anim_coord}:{new_node.id}'}),
                        dbc.Button(html.I(className="bi bi-skip-forward"),  color="light", id={"type":"last_frame",  "index":f'{anim_coord}:{new_node.id}'}),
                        ], size="sm",
                        ),
                ]) for anim_coord in coords
            ]

        if plot_type.is_animation() or plot_type == PlotType.FourD or plot_type == PlotType.ThreeD:
            # We need a way to track which figures generate 'click_data_list' data.
            # The chidren MUST be the ID, this H4 is used to identify the figure that clicked inside
            # HIddden
            header = html.H4(f"{new_node.id}", style={"backgroundColor": "yellow","display":"none"},
                                        id={"type": f"click_data_identifier", "index": new_node.id})
        else:
            header = html.H4(new_node.id, style={"backgroundColor": "lightblue","display":"none"})

        new_figure = dbc.Col(
                            [
                                header,
                                *frame_controls,
                                # Buttons with reduced pad and margin
                                html.Div([ dbc.Button("x", id={"type":"close_figure", "index":new_node.id}, color="danger"
                                                    , size="sm", className="mr-1 mb-1"),
                                            ], className="d-flex justify-content-end"),
                                fig,
                                *anim_options,
                            ],
                            id = f'figure:{new_node.id}',
                            width=col_width)

        return new_figure

    def create_profiles(self, parent_id, clicked_data, patch) -> list:

        parent_node = self.tree_root.locate(parent_id)
        data = parent_node.get_data()
        parent_node_id = parent_node.get_id()
        parent_field = parent_node.get_field_name()
        col_width = 4

        # We are assuming we made it to here because someone clicked on the map
        # so we need to plot a profile

        lon = clicked_data["points"][0]["x"]
        lat = clicked_data["points"][0]["y"]

        parent_coord_names = parent_node.get_coord_names()
        subset_data = select_spatial_location(data, lat, lon, parent_coord_names)
        dims = subset_data.dims

        for c_dim in dims:
            id = self.id_generator(f'{parent_node_id}_{c_dim}_prof')
            title = f'{parent_field} at {lat:0.2f}, {lon:0.2f} ({c_dim.capitalize()})' # type: ignore

            profile_data = select_profile(subset_data, c_dim, dims)
            
            new_node = ProfileNode(id, profile_data, lat, lon, c_dim, title, plot_type=PlotType.OneD, 
                                field_name=parent_field, parent=parent_node) # type: ignore

            parent_node.add_child(new_node) 
            fig = new_node.create_figure()
            
            header = html.H4(new_node.id, style={"backgroundColor": "lightblue"})

            new_figure = dbc.Col(
                                [
                                    header,
                                    # Buttons with reduced pad and margin
                                    html.Div([ dbc.Button("x", id={"type":"close_figure", "index":new_node.id}, color="danger"
                                                        , size="sm", className="mr-1 mb-1"),
                                                ], className="d-flex justify-content-end"),
                                    fig,
                                ],
                                id = f'figure:{new_node.id}',
                                width=col_width)

            patch.append(new_figure)

        return patch
        
    def get_field_names(self, field_dimension) -> list:
            '''
            This method returns the field names for a given dimension
            The dimension can be 1D, 2D, 3D or 4D
            '''
            dim_names = []
            if field_dimension == "1D":
                dim_names = self.one_d
            elif field_dimension == "2D":
                dim_names = self.two_d
            elif field_dimension == "3D":
                dim_names = self.three_d
            elif field_dimension == "4D":
                dim_names = self.four_d

            return [(x,str(self.data[x].shape)) for x in dim_names]

    # def get_field(self, field_name):
    #     '''
    #     This method returns the field for a given field name
    #     '''
    #     return self.data[field_name]

    def id_generator(self, field_name):
        '''
        This method returns an id for a given field name
        '''
        new_id = field_name
        count = 2
        while self.tree_root.locate(new_id) is not None:
            new_id = field_name + f'_{count}'
            count += 1

        return new_id
    
    def close_figure(self, node_id, prev_children, patch):
        '''
        This method closes an exising figure and removes the corresponing object from the tree. 
        '''
        # Iterate over the exisiting figures. Remember that on the interface there is
        # just 'one leve' tree. All the figures are on the 'same level'.
        for idx, c_child in enumerate(prev_children):
            # If we found the corresponding figure, remove it from the list of children
            if c_child['props']['id'].split(':')[1] == node_id:
                # print(f"Removing child {c_child['props']['id']}")
                del patch[idx]
                self.tree_root.remove_id(node_id)
                break

        return patch 

    def update_figure(self, idx, current_node: FigureNode, patch):

        '''
        This method creates a new animation figure.
        '''
        fig = current_node.create_figure()
        col_width = 4
        
        # If we have animation coords and we are not plotting an animation we make the buttons
        anim_options = []

        header = html.H4(f"{current_node.id}", style={"backgroundColor": "yellow"},
                                    id={"type": f"click_data_identifier", "index": current_node.id})

        new_figure = dbc.Col(
                            [
                                header,
                                *anim_options,
                                # Buttons with reduced pad and margin
                                html.Div([ dbc.Button("x", id={"type":"close_figure", "index":current_node.id}, color="danger"
                                                    , size="sm", className="mr-1 mb-1"),
                                            ], className="d-flex justify-content-end"),
                                fig,
                            ],
                            id = f'figure:{current_node.id}',
                            width=col_width)

        patch[idx] = new_figure

        return patch




    def create_animation_figure(self, parent_id, anim_coord, resolution, patch):
        '''
        This method creates a new animation figure.
        '''

        # TODO need to decide which plot type it is. Based on the parent type. If it was 
        # a 3D plot, then it should be a 3D animation. If it was a 4D plot, then it should be a 4D animation
        parent_node = self.tree_root.locate(parent_id)

        if parent_node.get_plot_type() == PlotType.ThreeD:
            plot_type = PlotType.ThreeD_Animation
        else:
            plot_type = PlotType.FourD_Animation
        
        data = parent_node.get_data()
        parent_node_id = parent_node.get_id()
        parent_field = parent_node.get_field_name()
        col_width = 4

        id = self.id_generator(f'{parent_node_id}_{anim_coord}_anim')
        new_node = AnimationNode(id, data, anim_coord, resolution, plot_type=plot_type, 
                            field_name=parent_field, parent=parent_node)# type: ignore

        parent_node.add_child(new_node) 
        fig = new_node.create_figure()
        
        # If we have animation coords and we are not plotting an animation we make the buttons
        anim_options = []

        header = html.H4(f"{new_node.id}", style={"backgroundColor": "yellow"},
                                    id={"type": f"click_data_identifier", "index": new_node.id})

        new_figure = dbc.Col(
                            [
                                header,
                                *anim_options,
                                # Buttons with reduced pad and margin
                                html.Div([ dbc.Button("x", id={"type":"close_figure", "index":new_node.id}, color="danger"
                                                    , size="sm", className="mr-1 mb-1"),
                                            ], className="d-flex justify-content-end"),
                                fig,
                            ],
                            id = f'figure:{new_node.id}',
                            width=col_width)

        patch.append(new_figure)

        return patch




# Main to test the class
if __name__ == '__main__':
    path = "./test_data/"
    regex = "hycom_gom.nc"
    obj = Dashboard(path, regex)