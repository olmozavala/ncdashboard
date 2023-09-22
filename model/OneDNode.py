# This is a the OneDNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used plot 1D data.

import numpy as np
import plotly.graph_objects as go
from dash import dcc

from model.TreeNode import FigureNode
from model.model_utils import PlotType
from model.model_utils import PlotType, get_all_coords
from proj_layout.utils import get_buttons_config


class OneDNode(FigureNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st dimensions may not be time, we are still calling it like that. 
    def __init__(self, id, data, title=None, field_name=None, 
                 bbox=None, plot_type = PlotType.FourD, parent=None,  cmap=None):

        super().__init__(id, data, title=title, field_name=field_name, bbox=bbox, 
                         plot_type=plot_type, parent=parent, cmap=cmap)

    def create_figure(self):
        dims = self.data.dims  # Get the list of dimensions
        profile = self.data.values  # Get the values of the data

        # Get the units of the coordinate
        try:
            units_y = self.data.units
        except:
            units_y = 'no units'

        # TODO Hack to flip the y axis if the dimension is depth and it is positive
        figure=go.Figure(
                data=[go.Scatter(x=list(range(len(profile))), y=profile, mode='lines+markers')], 
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
                        xaxis_title=f'Index',
                    ),
            )

        new_graph = dcc.Graph(
                id={"type": "figure_1d", "index": self.id},
                figure=figure,
                config=get_buttons_config(),
        )
        return new_graph