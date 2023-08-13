import json
from textwrap import dedent as d

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, ctx, Input, Output, State, ALL, callback, Patch
from dash.exceptions import PreventUpdate
import numpy as np

from model.dashboard import Dashboard
from model.TreeNode import PlotType
from model.model_utils import print_tree

path = "/home/olmozavala/Dropbox/MyGrants/2022/FYAP/ncdashboard/test_data/"
# regex = "hycom_gom.nc"
# path = "/home/olmozavala/Dropbox/TestData/netCDF/GoM"
# path = "/unity/f1/ozavala/DATA/GOFFISH/AVISO/GoM"
regex = "gom_*.nc"

# path = "/unity/f1/ozavala/DATA/GOFFISH/CHLORA/CICESE_NEMO_GOM_RAW"
# path = "/unity/f1/ozavala/DATA/GOFFISH/CHLORA/CICESE_NEMO_GOM_RAW/"
# regex = "*ptrc*.nc"
# regex = "GOM36-ERA5_0_1d_20180322_20180719_ptrc_T.nc"

# path = "/unity/f1/ozavala/DATA/GOFFISH/CHLORA/NOAA"
# regex = "*.nc"

ncdash = Dashboard(path, regex)

# https://dash.plotly.com/sharing-data-between-callbacks
app = dash.Dash( __name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.5.0/font/bootstrap-icons.min.css", # Bootstrap Icons
                                                 ], suppress_callback_exceptions=True,)

def initial_menu():
    return [
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

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("NcDashboard", style={"textAlign": "center"}),

                    ],
                    width={"size": 6, "offset": 3},
                )
            ]
        ),
        dbc.Row(
            initial_menu(),
            id="start_menu"
        ),

        dbc.Row(
            [
                dbc.Col(
                    [ 
                        dbc.Button("Plot selected fileds", id="but_plot_all", color="success", size='lg'),
                        dcc.Loading(
                            id="loading-1",
                            children=[html.Div(id="loading-output-1")],
                            type="circle",
                        ),
                    ], width={"size": 6, "offset": 4}),
            ]
        ),
        dbc.Row([], id="display_area"),
    ],
    fluid=True,
    id="container",
)

@callback(
    Output("start_menu", "children"),
    Input("but_plot_all", "n_clicks"),
)
def clear_selected(n_clicks):
    return initial_menu()

@callback(
    Output("display_area", "children"),
    Output("loading-output-1", "children"),
    State("display_area", "children"),
    State("1D_vars", "value"),
    State("2D_vars", "value"),
    State("3D_vars", "value"),
    State("4D_vars", "value"),
    Input("but_plot_all", "n_clicks"),
    State({"type": "click_data_identifier", "index": ALL}, 'children'),
    # Input("but_plot_together", "n_clicks"),
    Input({"type": "animation", "index": ALL}, "n_clicks"),
    Input({"type": "resolution", "index": ALL}, "value"),
    Input({"type": "close_figure", "index": ALL}, "n_clicks"),
    Input({"type": "figure", "index":ALL}, 'clickData'),
    Input({"type": "figure", "index":ALL}, 'relayoutData'),
)
def display_relayout_data(prev_children, selected_1d, selected_2d, selected_3d, selected_4d, 
                          n_clicks_plot_separated, click_data_identifiers,
                          n_clicks_requestanimation,
                          resolution_list, close_list, click_data_list, selected_data_list):

    triggered_id = ctx.triggered_id
    print(f'Type: {type(triggered_id)}, Value: {triggered_id}')

    print(f'1D: {selected_1d}, 2D: {selected_2d}, 3D: {selected_3d}, 4D: {selected_4d}')
    # Check the one trigered was but_plot_all

    patch = Patch()
    plot_types = [PlotType.OneD, PlotType.TwoD, PlotType.ThreeD, PlotType.FourD]
            
    # Initial case, do nothing
    if triggered_id == None:
        return [], []
    # First level plots, directly from the menu
    elif triggered_id == 'but_plot_all':
        for i, selected in enumerate([selected_1d, selected_2d, selected_3d, selected_4d]):
            if selected!= None and len(selected) > 0:
                new_figures = ncdash.create_first_level_figure(selected, plot_types[i])
                for c_figure in new_figures:
                    patch.append(c_figure)

    # Closing a plot
    elif type(triggered_id) == dash._utils.AttributeDict and triggered_id['type'] == 'close_figure': # type: ignore
        # print("------------------------- Closing figure! ----------------")
        node_id = triggered_id['index']
        patch = ncdash.close_figure(node_id, prev_children, patch)

    # Create animations
    elif type(triggered_id) == dash._utils.AttributeDict and triggered_id['type'] == 'animation': # type: ignore
        button_index = triggered_id['index'].split(":")
        node_id = button_index[0]
        anim_coord = button_index[1]
        resolution = [x.split(':')[1] for x in resolution_list if x.split(':')[0] == node_id][0] 
        patch = ncdash.create_animation_figure(node_id, anim_coord, resolution, patch)

    # Second level plots clicked on map (should generate profile)
    elif type(triggered_id) == dash._utils.AttributeDict and triggered_id['type'] == 'figure': # type: ignore
        # Check if it was a relayout event
        if ctx.triggered[0]['prop_id'].find('relayoutData') != -1:
            print(f'Selected data: {selected_data_list}')
        else:
            print(click_data_list)
            node_id = triggered_id['index'].split(":")[0]
            data_identifiers = np.array([x.split(':')[0] for x in click_data_identifiers])
            click_index = np.where(data_identifiers == node_id)[0][0]
            # TODO need to decide which plot type it is. Based on the parent type. If it was 
            # a 3D plot, then it should be a 3D animation. If it was a 4D plot, then it should be a 4D animation
            parent_node = ncdash.tree_root.locate(node_id)
            plot_type = PlotType.OneD

            # TODO here we should also modify the original plot and add a dot where the user clicked
            click_data= click_data_list[click_index]
            
            patch = ncdash.create_profiles(node_id, plot_type, click_data, patch)

    elif len(prev_children) == 0:
        return html.Div('mydiv', style={"backgroundColor": "blue", "color": "white"}), []
    else: 
        return prev_children, []

    print_tree(ncdash.tree_root)
    return patch, []

if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(debug=False, port=8080, host='146.201.212.115')
    # app.run_server(debug=False, port=8051, host='144.174.7.151')
