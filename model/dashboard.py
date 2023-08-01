import xarray as xr
from os.path import join
from model.dashboardstate import TreeNode
import dash_bootstrap_components as dbc

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
        # In this case we need to create buttons: time and xaxis
        anim_buttons = dbc.ButtonGroup(
                        [ dbc.Button(f'Animate {anim_coord}', 
                                     id={"type": "animation", 
                                         "index": f'{node.id}:{anim_coord}'}) 
                                         for anim_coord in coords],
                        size="sm",
                    )

        new_figure = dbc.Col(
                        [
                            anim_buttons,
                            fig,
                            dbc.Button(
                                f"{node.id}",
                                id={"type": f"fig_button", "index": node.id},
                            )
                        ],
                        # style={"background-color": "lightblue"},
                        width=width)
        return new_figure

    def create_first_level_figure(self, prev_layout, selected_fields, plot_type):

        new_col = []
        col_width = 4

        for c_field in selected_fields:
            id = self.id_generator(c_field)
            new_node = TreeNode(id, self.data[c_field], plot_type=plot_type, 
                                field_name=c_field, parent=self.tree_root) # type: ignore
            self.tree_root.add_child(new_node) # type: ignore
            new_col.append(self.add_field(col_width, new_node))

        if len(prev_layout) == 0:  # Return a new column
            return [dbc.Row(new_col)]
        else:
            prev_layout[0]["props"]["children"] = prev_layout[0]["props"][
                "children"
            ] + new_col
            return prev_layout

    def create_deeper_level_figure(self, prev_layout, parent_id, plot_type, anim_coord=None):

        new_col = []

        parent_node = self.tree_root.locate(parent_id)
        data = parent_node.get_data()
        parent_node_id = parent_node.get_id()
        parent_field = parent_node.get_field_name()
        col_width = 4

        if plot_type.is_animation():
            id = f'{parent_node_id}_{anim_coord}_anim'
            new_node = TreeNode(id, data, plot_type=plot_type, 
                                field_name=parent_field, parent=parent_node,
                                animation=True, anim_coord_name=anim_coord) 
            parent_node.add_child(new_node) 
            new_col.append(self.add_field(col_width, new_node))

        if len(prev_layout) == 0:  # Return a new column
            return [dbc.Row(new_col)]
        else:
            prev_layout[0]["props"]["children"] = prev_layout[0]["props"][
                "children"
            ] + new_col
            return prev_layout


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
        return field_name



# Main to test the class
if __name__ == '__main__':
    path = "./test_data/"
    regex = "hycom_gom.nc"
    obj = Dashboard(path, regex)