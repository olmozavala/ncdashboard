import xarray as xr
from os.path import join
from model.dashboardstate import TreeNode
import dash_bootstrap_components as dbc
from dash import Patch, html, dcc
from model.model_utils import PlotType

from proj_layout.utils import get_buttons_config, get_def_slider, get_update_buttons, select_colormap

# Make a class with attributes and methods to create a dashboard

class Dashboard:
    def __init__(self, path, regex):
        self.path = path
        self.regex = regex
        data = xr.open_mfdataset(join(self.path, self.regex), decode_times=False)
        self.tree_root = TreeNode('root', data=data, parent=None) # type: ignore
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

    def add_field(self, width, node: TreeNode):

        fig = node.create_figure()
        plot_type = node.get_plot_type()
        
        coords = node.get_animation_coords()
        # If we have animation coords and we are not plotting an animation we make the buttons
        anim_options = []
        if len(coords) > 0 and not plot_type.is_animation():
            anim_options = [
                dbc.Row( 
                    [
                        dbc.Col( html.Div("Resolution:"), width=3),
                        dbc.Col( dbc.RadioItems(
                                    id={"type": "resolution",
                                        "index": node.id},
                                    options=[
                                        {"label": "High", "value": f"{node.id}:high"},
                                        {"label": "Medium", "value": f"{node.id}:medium"},
                                        {"label": "Low", "value": f"{node.id}:low"},
                                    ],
                                    value=f"{node.id}:low",
                                    inline=True,
                                ),
                            width=9),
                    ]
                ),
                dbc.Row(
                    dbc.Col(
                            [ dbc.Button(f'Animate {anim_coord}', 
                                        id={"type": "animation", 
                                            "index": f'{node.id}:{anim_coord}'},
                                        size="sm",
                                        className="me-1",
                                        color='light'
                                        ) 
                                        for anim_coord in coords ],
                        width={'size':8, 'offset':2},
                        )
                    ),
            ]

        if plot_type.is_animation() or plot_type == PlotType.FourD or plot_type == PlotType.ThreeD:
            # We need a way to track which figures generate 'click_data_list' data.
            # The chidren MUST be the ID, this H4 is used to identify the figure that clicked inside
            header = html.H4(f"{node.id}", style={"background-color": "yellow"},
                                        id={"type": f"click_data_identifier", "index": node.id})
        else:
            header = html.H4(node.id, style={"background-color": "lightblue"})

        new_figure = dbc.Col(
                            [
                                header,
                                *anim_options,
                                # Buttons with reduced pad and margin
                                html.Div([ dbc.Button("x", id={"type":"close_figure", "index":node.id}, color="danger"
                                                    , size="sm", className="mr-1 mb-1"),
                                            ], className="d-flex justify-content-end"),
                                fig,
                                # dbc.Button(
                                #     f"{node.id}",
                                #     id={"type": f"fig_button", "index": node.id},
                                # )
                            ],
                            # style={"background-color": "lightblue"},
                            id = f'figure:{node.id}',
                            width=width)

        return new_figure

    def create_first_level_figure(self, selected_fields, plot_type) -> list:

        new_figures = []
        col_width = 4

        for c_field in selected_fields:
            id = self.id_generator(c_field)
            new_node = TreeNode(id, self.data[c_field], plot_type=plot_type, 
                                field_name=c_field, parent=self.tree_root) # type: ignore
            self.tree_root.add_child(new_node) # type: ignore
            new_figures.append(self.add_field(col_width, new_node))

        return new_figures


    def create_deeper_level_figure(self, parent_id, plot_type, 
                                   anim_coord=None, 
                                   resolution=None,
                                   clicked_data=None) -> list:

        new_figures = []

        parent_node = self.tree_root.locate(parent_id)
        data = parent_node.get_data()
        parent_node_id = parent_node.get_id()
        parent_field = parent_node.get_field_name()
        col_width = 4

        if plot_type.is_animation():
            id = f'{parent_node_id}_{anim_coord}_anim'
            new_node = TreeNode(id, data, plot_type=plot_type, 
                                field_name=parent_field, parent=parent_node,
                                animation=True, anim_coord_name=anim_coord, 
                                spatial_res=resolution) # type: ignore
            parent_node.add_child(new_node) 
            new_figures.append(self.add_field(col_width, new_node))

        if plot_type == PlotType.OneD:
            # We are assuming we made it to here because someone clicked on the map
            # so we need to plot a profile
            id = self.id_generator(f'{parent_node_id}_prof')
            coords = parent_node.get_coord_names()

            lon = clicked_data["points"][0]["x"]
            lat = clicked_data["points"][0]["y"]

            # We are assuming that the last two coords are always lat and lon
            data = data.sel({coords[-2]:lat, coords[-1]:lon}, method="nearest") 
            title = f'{parent_field} at {lat:0.2f}, {lon:0.2f}'
            new_node = TreeNode(id, data, title, plot_type=plot_type, 
                                field_name=parent_field, parent=parent_node) # type: ignore
            parent_node.add_child(new_node) 
            new_figures.append(self.add_field(col_width, new_node))

        return new_figures
        
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

    def get_field(self, field_name):
        '''
        This method returns the field for a given field name
        '''
        return self.data[field_name]

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



# Main to test the class
if __name__ == '__main__':
    path = "./test_data/"
    regex = "hycom_gom.nc"
    obj = Dashboard(path, regex)