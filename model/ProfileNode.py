#Similar to AnimationNode, its a class that inherits from TreeNode. In this case it manages
# figures that will generate a profile plot. 


import numpy as np
import plotly.graph_objects as go
from dash import dcc

from model.TreeNode import FigureNode
from model.model_utils import PlotType, Resolutions
from model.model_utils import PlotType, get_all_coords, select_anim_data
from proj_layout.utils import get_buttons_config, get_def_slider, get_update_buttons, select_colormap


class ProfileNode(FigureNode):

    def __init__(self, id, data, lat, lon, profile_coord, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.OneD, parent=None,  cmap=None):

        super().__init__(id, data, title=title, field_name=field_name, bbox=bbox, 
                         plot_type=plot_type, parent=parent, cmap=cmap)

        self.lat = lat
        self.lon = lon
        self.profile_coord = profile_coord

    def create_figure(self):
        
        dims = self.data.dims  # Get the list of dimensions
        profile = self.data.values  # Get the values of the data
        coordinate = self.data.coords[self.profile_coord]  # Get the coordinate

        # Get the units of the coordinate
        try:
            units_y = coordinate.units
        except:
            units_y = 'no units'

        # TODO Hack to flip the y axis if the dimension is depth and it is positive
        if self.profile_coord.lower() == 'depth':
            # TODO hardcoded that if it is depth we flip the y axis
            if coordinate.values[1] > coordinate.values[0]:
                coordinate = -coordinate

            figure=go.Figure(
                    data=[go.Scatter(x=profile, y=coordinate.values, mode='lines+markers')], 
                    layout=go.Layout(
                            title=self.title, 
                            title_x=0.5,
                            height=350,
                            margin=dict(
                                l=0,  # left margin
                                r=0,  # right margin
                                b=0,  # bottom margin
                                t=30,  # top margin
                                pad=0  # padding
                            ),
                            yaxis_title=f'{dims[-1].capitalize()} ({units_y})',
                            xaxis_title=f'{self.long_name} ({self.units})',
                        ),
                )
        else:
            figure=go.Figure(
                    data=[go.Scatter(x=coordinate.values, y=profile, mode='lines+markers')], 
                    layout=go.Layout(
                            title=self.title, 
                            title_x=0.5,
                            height=350,
                            margin=dict(
                                l=0,  # left margin
                                r=0,  # right margin
                                b=0,  # bottom margin
                                t=30,  # top margin
                                pad=0  # padding
                            ),
                            yaxis_title=f'{self.long_name} ({self.units})',
                            xaxis_title=f'{dims[-1].capitalize()} ({units_y})',
                        ),
                )


        new_graph = dcc.Graph(
                id={"type": "figure_1d", "index": self.id},
                figure=figure,
                config=get_buttons_config(),
        )
        return new_graph


