import dash
from dash import dcc, html, ctx, Input, Output, State, ALL, callback, Patch
import logging
from model.TreeNode import PlotType
from model.model_utils import print_tree
from textwrap import dedent as d
from dash import dcc, html, ctx, Input, Output, State, ALL, callback, Patch
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from model.dashboard import Dashboard
import numpy as np

class NcDashboard:
    app = app = dash.Dash( __name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
    # "bootstrap-icons.min.css", # Bootstrap Icons
    "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.5.0/font/bootstrap-icons.min.css", # Bootstrap Icons
                                                 ], suppress_callback_exceptions=True)
 
    def __init__(self, file_paths, regex, host = '127.0.0.1', port = 8050):

        self.host = host
        self.port = port

        logging.info('Starting NcDashboard...')
        self.ncdash = Dashboard(file_paths, regex)

        self.app.layout = dbc.Container(
            [
                dcc.Store(id='window-size'),
                html.Div(id='output-div'),
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
                    self.initial_menu(),
                    id="start_menu"
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            [ 
                                dbc.Button("Plot selected fields", id="but_plot_all", color="success", size='lg'),
                                dbc.Button("Close all", id="but_close_all", color="danger", size='lg', className="ms-2"),
                                dcc.Download(id="download-data"),
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
        self.register_callbacks()

    def start(self):
        self.app.run_server(debug=False, port=self.port, host=self.host)

    def initial_menu(self):
        return [
                    dbc.Col( # Creates multiple checklist, one for each type of variable supported (1D, 2D, 3D, 4D)
                        [
                            html.H2(f"{var_type} Vars"),
                            dbc.Checklist(
                                id=f"{var_type}_vars",
                                options=[{"label": f'{name} {dims}', "value": field} for name, field, dims in self.ncdash.get_field_names(var_type)],
                                inline=False,
                            ),
                        ]
                    ) for var_type in ["4D", "3D", "2D", "1D"]
                ]

    def register_callbacks(self):
        @self.app.callback(
            Output("start_menu", "children"),
            Input("but_plot_all", "n_clicks"),
        )
        def clear_selected(n_clicks):
            return self.initial_menu()

        @self.app.callback(
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
            Input({"type": "download_data", "index": ALL}, "n_clicks"),
            Input({"type": "figure", "index":ALL}, 'clickData'),
            Input({"type": "figure", "index":ALL}, 'relayoutData'),
            Input({"type": "first_frame", "index":ALL}, 'n_clicks'),
            Input({"type": "prev_frame", "index":ALL}, 'n_clicks'),
            Input({"type": "next_frame", "index":ALL}, 'n_clicks'),
            Input({"type": "last_frame", "index":ALL}, 'n_clicks'),
            Input('window-size', 'data')
        )
        def display_relayout_data(prev_children, selected_1d, selected_2d, selected_3d, selected_4d, 
                                n_clicks_plot_separated, click_data_identifiers,
                                n_clicks_requestanimation, resolution_list, close_list, download_list,
                                click_data_list, selected_data_list,
                                    n_clicks_first_frame, n_clicks_prev_frame, n_clicks_next_frame, n_clicks_last_frame,
                                    window_size):

            # TODO we need to be able to separate this function, at least to call methods somewhere else 
            window_ratio = 0.8
            if window_size is None:
                print("Window size information is not available.")
            else:
                width = window_size.get('width', 'Unknown')
                height = window_size.get('height', 'Unknown')
                window_ratio = width/height
                # print width, height
                print(f"Window Width: {width}, Window Height: {height}")

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

                        for c_field in selected:
                            new_figure = self.ncdash.create_default_figure(c_field, plot_types[i])
                            patch.append(new_figure)

            # Closing a plot
            elif type(triggered_id) == dash._utils.AttributeDict and triggered_id['type'] == 'close_figure': # type: ignore
                # print("------------------------- Closing figure! ----------------")
                node_id = triggered_id['index']
                patch = self.ncdash.close_figure(node_id, prev_children, patch)

            elif type(triggered_id) == dash._utils.AttributeDict and triggered_id['type'] == 'download_data': # type: ignore
                # print("------------------------- Downloading data! ----------------")
                node_id = triggered_id['index']
                # patch = self.ncdash.close_figure(node_id, prev_children, patch)
                if ctx.triggered[0]['prop_id'].find('relayoutData') != -1:
                    print(f'Selected data: {selected_data_list}')

            # Next frame
            elif type(triggered_id) == dash._utils.AttributeDict and (triggered_id['type'] == 'next_frame' or triggered_id['type'] == 'prev_frame' or  # type: ignore
            triggered_id['type'] == 'first_frame' or triggered_id['type'] == 'last_frame'): # type: ignore
            
                index = triggered_id['index'].split(":")
                coord = index[0]
                node_id = index[1]
                node = self.ncdash.tree_root.locate(node_id)

                coords = node.get_animation_coords()

                # --------------- This part should be the same for all ------------
                # Get the index of the coordinate
                coord_index = coords.index(coord)

                # First index should always be time (it doesn't matter if the name is other)
                if triggered_id['type'] == 'next_frame':
                    if coord_index == 0: # For 4D first index 
                        node.next_time()
                    if coord_index == 1 and node.get_plot_type() == PlotType.FourD: # For 4D first index 
                        node.next_depth()
                elif triggered_id['type'] == 'prev_frame':
                    if coord_index == 0:
                        node.prev_time()
                    if coord_index == 1 and node.get_plot_type() == PlotType.FourD: # For 4D first index
                        node.prev_depth()
                elif triggered_id['type'] == 'first_frame':
                    if coord_index == 0:
                        node.set_time_idx(0)
                    if coord_index == 1 and node.get_plot_type() == PlotType.FourD: # For 4D first index
                        node.set_depth_idx(0)
                elif triggered_id['type'] == 'last_frame':
                    if coord_index == 0:
                        node.set_time_idx(-1)
                    if coord_index == 1 and node.get_plot_type() == PlotType.FourD:
                        node.set_depth_idx(-1)
                
                # Update the figure
                for idx, c_child in enumerate(prev_children):
                    # If we found the corresponding figure, remove it from the list of children
                    if c_child['props']['id'].split(':')[1] == node_id:
                        # print(f"Removing child {c_child['props']['id']}")

                        updated_figure = self.ncdash.create_default_figure(node.get_field_name(), node.get_plot_type(), node)
                        patch[idx] = updated_figure
                        break

            # Create animations
            elif type(triggered_id) == dash._utils.AttributeDict and triggered_id['type'] == 'animation': # type: ignore
                button_index = triggered_id['index'].split(":")
                node_id = button_index[0]
                anim_coord = button_index[1]
                resolution = [x.split(':')[1] for x in resolution_list if x.split(':')[0] == node_id][0] 
                patch = self.ncdash.create_animation_figure(node_id, anim_coord, resolution, patch)

            # Second level plots (someone clicked on map)
            elif type(triggered_id) == dash._utils.AttributeDict and triggered_id['type'] == 'figure': # type: ignore
                # Check if it was a relayout event
                if ctx.triggered[0]['prop_id'].find('relayoutData') != -1:
                    print(f'Selected data: {selected_data_list}')
                else:
                    #  (should generate profile)
                    print(click_data_list)
                    node_id = triggered_id['index'].split(":")[0]
                    data_identifiers = np.array([x.split(':')[0] for x in click_data_identifiers])
                    click_index = np.where(data_identifiers == node_id)[0][0]

                    # TODO here we should also modify the original plot and add a dot where the user clicked
                    click_data= click_data_list[click_index]
                    
                    patch = self.ncdash.create_profiles(node_id, click_data, patch)

            elif len(prev_children) == 0:
                return html.Div('', style={"backgroundColor": "blue", "color": "white"}), []
            else: 
                return prev_children, []

            print_tree(self.ncdash.tree_root)
            return patch, []

        @self.app.callback(
            Output("display_area", "children"),
            Input("but_close_all", "n_clicks"),
            State("display_area", "children"),
            prevent_initial_call=True
        )
        def close_all_figures(n_clicks, prev_children):
            if n_clicks:
                self.ncdash.tree_root.children = []  # Clear all children from the tree
                return []  # Return empty list to clear all figures
            return prev_children

        self.app.clientside_callback(
            """
            function(n_clicks) {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight
                };
            }
            """,
            Output('window-size', 'data'),
            Input("but_plot_all", "n_clicks"),
        )