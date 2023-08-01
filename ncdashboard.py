import json
from textwrap import dedent as d

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, ctx, Input, Output, State, ALL, callback
from dash.exceptions import PreventUpdate
import numpy as np

from model.dashboard import Dashboard
from model.dashboardstate import PlotType

# path = "/home/olmozavala/Dropbox/MyGrants/2022/FYAP/ncdashboard/test_data/"
# regex = "hycom_gom.nc"
path = "/home/olmozavala/Dropbox/TestData/netCDF/GoM"
regex = "*.nc"
ncdash = Dashboard(path, regex)

# https://dash.plotly.com/sharing-data-between-callbacks
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(

                    html.H1("NcDashboard", style={"textAlign": "center"}),
                    width={"size": 6, "offset": 3},
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col( # Creates multiple checklist, one for each type of variable supported (1D, 2D, 3D, 4D)
                    [
                        html.H2(f"{var_type} Vars"),
                        dbc.Checklist(
                            id=f"{var_type}_vars",
                            options=[{"label": f'{field} {dims}', "value": field} for field, dims in ncdash.get_field_names(var_type)],
                            inline=False,
                        ),
                    ]
                ) for var_type in ["4D", "3D", "2D", "1D"]
            ]
        ),

        dbc.Row(
            [
                dbc.Col(
                    [ 
                        dbc.Button("Plot Separated", id="but_plot_all", color="secondary"),
                    ], width={"size": 4, "offset": 2}),
                dbc.Col(
                    [ 
                        dbc.Button("Plot Together", id="but_plot_together", color="secondary"),
                    ], width={"size": 4, "offset": 2}),
            ]
        ),
        dbc.Row(dbc.Col(
            [

            ], width=12, id="display_area")),
    ],
    fluid=True,
    id="container",
)

@callback(
    Output("display_area", "children"),
    State("display_area", "children"),
    State("1D_vars", "value"),
    State("2D_vars", "value"),
    State("3D_vars", "value"),
    State("4D_vars", "value"),
    Input("but_plot_all", "n_clicks"),
    Input("but_plot_together", "n_clicks"),
    Input({"type": "animation", "index": ALL}, "n_clicks"),
)
def display_relayout_data(prev_children, selected_1d, selected_2d, selected_3d, selected_4d, 
                          n_clicks_plot_separated, n_clicks_plot_together, n_clicks_requestanimation):
    triggered_id = ctx.triggered_id
    print(f'Type: {type(triggered_id)}, Value: {triggered_id}')

    print(f'1D: {selected_1d}, 2D: {selected_2d}, 3D: {selected_3d}, 4D: {selected_4d}')
    # Check the one trigered was but_plot_all

    ret = html.Div('mydiv', style={"backgroundColor": "blue", "color": "white"})

    if triggered_id == None:
        return []
    if triggered_id == 'but_plot_all':
        # If 1D are not none
        if selected_1d != None:
            print('1D')

        if selected_2d != None:
            print('2D')

        if selected_3d != None:
            print('3D')
            ret = ncdash.create_first_level_figure(prev_children, selected_3d, PlotType.ThreeD)

        if selected_4d != None:
            print('4D')
            ret = ncdash.create_first_level_figure(prev_children, selected_4d, PlotType.FourD)

    if type(triggered_id) == dash._utils.AttributeDict and triggered_id['type'] == 'animation':
        button_index = triggered_id['index'].split(":")
        node_id = button_index[0]
        anim_coord = button_index[1]
        # TODO need to decide which plot type it is. Based on the parent type. If it was 
        # a 3D plot, then it should be a 3D animation. If it was a 4D plot, then it should be a 4D animation
        parent_node = ncdash.tree_root.locate(node_id)
        if parent_node.get_plot_type() == PlotType.ThreeD:
            plot_type = PlotType.ThreeD_Animation
        else:
            plot_type = PlotType.FourD_Animation
        ret = ncdash.create_deeper_level_figure(prev_children, node_id, plot_type, anim_coord)

    return ret

#             # Get the first level of children. Verify how many rows (children) are in the first level
#             # If there are no childrens, create a new Row. If there are childrens, add a new column
#     else:
#         curr_level = int(triggered_id["type"].split("_")[1])
#         lev2_clicks = np.array(lev2_n_clicks_all, dtype=np.float16)
#         lev2_clicks[lev2_clicks == None] = np.nan
#         max_lev2_clicks = np.nansum(lev2_clicks)
#         new_col = add_field(curr_level + 1, int(max_lev2_clicks), 2)
#         if (
#             len(prev_children) <= curr_level
#         ):  # In this case we don't have columns on the desired level
#             return prev_children + [dbc.Row([new_col])]
#         else:
#             prev_children[curr_level]["props"]["children"] = prev_children[curr_level][
#                 "props"
#             ]["children"] + [new_col]
#             return prev_children


if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(debug=False, port=8051, host='144.174.7.151')
