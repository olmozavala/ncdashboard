# This is a the ThreeDNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used plot 4D data.

import holoviews as hv
import panel as pn

from model.FigureNode import FigureNode
from model.model_utils import PlotType, get_all_coords
from loguru import logger

class ThreeDNode(FigureNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st dimensions may not be time, we are still calling it like that. 
    def __init__(self, id, data, coord_idx=0, plot_type=PlotType.ThreeD, 
                 title=None, field_name=None, bbox=None, parent=None, cmap=None):

        super().__init__(id, data, title=title, field_name=field_name, 
                         bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap)

        self.coord_idx = coord_idx
        logger.info(f"Created ThreeDNode: id={id}, shape={data.shape}, coords={self.coord_names}")
        self.third_coord_name = data.coords[self.coord_names[0]].name
        
        # Stream for dynamic updates
        self.update_stream = hv.streams.Stream.define('Update')()

    def _render_plot(self, **kwargs):
        colormap = self.cmap
        
        data = self.data
        if self.plot_type == PlotType.ThreeD:
            # We assume logical structure [time, lat, lon] for 3D
            # Select the time slice
            data = self.data[self.coord_idx, :, :]

        # We assume the last two coordinates are spatial (lat, lon)
        lats = data.coords[self.coord_names[-2]].values
        lons = data.coords[self.coord_names[-1]].values

        title = f'{self.title} at {self.coord_names[0].capitalize()} {self.coord_idx}'

        img = hv.Image((lons, lats, data), [self.coord_names[-1], self.coord_names[-2]])
        img.opts(
            cmap=colormap,
            title=title,
            tools=['hover'],
            colorbar=True,
            responsive=True,
            aspect='equal'
        )
        return img

    def create_figure(self):
        # Return a DynamicMap that updates when update_stream is triggered
        return hv.DynamicMap(self._render_plot, streams=[self.update_stream])

    def next_slice(self):
        self.coord_idx = (self.coord_idx + 1) % len(self.data[self.coord_names[0]])
        self.update_stream.event()
        return self.coord_idx
    
    def prev_slice(self):
        self.coord_idx = (self.coord_idx - 1) % len(self.data[self.coord_names[0]])
        self.update_stream.event()
        return self.coord_idx

    def set_coord_idx(self, coord_idx):
        self.coord_idx = coord_idx
        self.update_stream.event()
        
    def get_coord_idx(self):
        return self.coord_idx

    def first_slice(self):
        self.coord_idx = 0
        self.update_stream.event()
        return self.coord_idx

    def last_slice(self):
        self.coord_idx = len(self.data[self.coord_names[0]]) - 1
        self.update_stream.event()
        return self.coord_idx

    def get_controls(self):
        btn_style = {'margin': '0px 2px'}
        # Using FontAwesome icons as requested
        btn_first = pn.widgets.Button(name="\u00ab", icon="angles-left", width=40, height=30, styles=btn_style)
        btn_prev = pn.widgets.Button(name="\u2039", icon="angle-left", width=40, height=30, styles=btn_style)
        btn_next = pn.widgets.Button(name="\u203a", icon="angle-right", width=40, height=30, styles=btn_style)
        btn_last = pn.widgets.Button(name="\u00bb", icon="angles-right", width=40, height=30, styles=btn_style)

        def on_first(event):
            self.first_slice()
        
        def on_prev(event):
            self.prev_slice()

        def on_next(event):
            self.next_slice()

        def on_last(event):
            self.last_slice()

        btn_first.on_click(on_first)
        btn_prev.on_click(on_prev)
        btn_next.on_click(on_next)
        btn_last.on_click(on_last)
        
        nav_row = pn.Row(
            pn.layout.HSpacer(),
            btn_first, btn_prev, btn_next, btn_last,
            pn.layout.HSpacer(),
            align='center'
        )
        return nav_row
