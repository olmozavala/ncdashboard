# This is a the ThreeDNode class, which inherits from the FigureNode class.
# It is used to create a node that can be used plot 4D data.

import holoviews as hv
import geoviews as gv
import panel as pn
import cartopy.crs as ccrs
from holoviews.operation.datashader import rasterize

from model.FigureNode import FigureNode
from model.model_utils import PlotType, get_all_coords
from loguru import logger

class ThreeDNode(FigureNode):
    # This is the constructor for the AnimationNode class. It calls its parent's constructor.
    # It also sets the animation coordinate and the resolution of the animation.
    # Eventhough the 1st dimensions may not be time, we are still calling it like that. 
    def __init__(self, id, data, third_coord_idx=0, plot_type=PlotType.ThreeD, 
                 title=None, field_name=None, bbox=None, parent=None, cmap=None):

        super().__init__(id, data, title=title, field_name=field_name, 
                         bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap)

        self.third_coord_idx = third_coord_idx
        logger.info(f"Created ThreeDNode: id={id}, shape={data.shape}, coords={self.coord_names}")
        self.third_coord_name = data.coords[self.coord_names[0]].name
        
        # Stream for dynamic updates
        self.update_stream = hv.streams.Counter()

    def _render_plot(self, counter=0, **kwargs):
        colormap = self.cmap
        
        data = self.data
        if self.plot_type == PlotType.ThreeD:
            # We assume logical structure [time, lat, lon] for 3D
            # Select the time slice
            data = self.data[self.third_coord_idx, :, :]

        # We assume the last two coordinates are spatial (lat, lon)
        lats = data.coords[self.coord_names[-2]].values
        lons = data.coords[self.coord_names[-1]].values

        title = f'{self.title} at {self.coord_names[0].capitalize()} {self.third_coord_idx}'

        # Use geoviews Image for geographic plotting
        img = gv.Image((lons, lats, data.values), [self.coord_names[-1], self.coord_names[-2]], crs=ccrs.PlateCarree())
        return img.opts(title=title, cmap=colormap)

    def create_figure(self):
        # Create a stream for the plot range to allow re-rasterization on zoom
        self.range_stream = hv.streams.RangeXY()
        
        # We wrap the rendering, rasterization and tiles in a single DynamicMap 
        # to avoid nesting DynamicMaps (which happens if you rasterize a DynamicMap 
        # and then overlay it with tiles in some Panel/HoloViews versions).
        
        def dynamic_plot(counter=0, x_range=None, y_range=None):
            # 1. Get the base plot for the current slice
            img = self._render_plot(counter=counter)
            
            # 2. Apply rasterization. 
            rasterized = rasterize(img, x_range=x_range, y_range=y_range, dynamic=False).opts(
                cmap=self.cmap,
                colorbar=True,
                tools=['hover']
            )
            
            # 3. Add tiles
            tiles = gv.tile_sources.OSM()
            return (tiles * rasterized).opts(
                responsive=True,
                aspect='equal'
            )

        self.dmap = hv.DynamicMap(dynamic_plot, streams=[self.update_stream, self.range_stream])
        
        return self.dmap.opts(active_tools=['wheel_zoom', 'pan'])

    def get_stream_source(self):
        if not hasattr(self, 'dmap'):
            self.create_figure()
        return self.dmap

    def next_slice(self):
        self.third_coord_idx = (self.third_coord_idx + 1) % len(self.data[self.coord_names[0]])
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.third_coord_idx
    
    def prev_slice(self):
        self.third_coord_idx = (self.third_coord_idx - 1) % len(self.data[self.coord_names[0]])
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.third_coord_idx

    def set_third_coord_idx(self, third_coord_idx):
        self.third_coord_idx = third_coord_idx
        self.update_stream.event(counter=self.update_stream.counter + 1)
        
    def get_third_coord_idx(self):
        return self.third_coord_idx

    def first_slice(self):
        self.third_coord_idx = 0
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.third_coord_idx

    def last_slice(self):
        self.third_coord_idx = len(self.data[self.coord_names[0]]) - 1
        self.update_stream.event(counter=self.update_stream.counter + 1)
        return self.third_coord_idx

    def _make_nav_controls(self, first_cb, prev_cb, next_cb, last_cb, label=None):
        btn_style = {'margin': '0px 2px'}
        btn_first = pn.widgets.Button(name="\u00ab", icon="angles-left", width=40, height=30, styles=btn_style)
        btn_prev = pn.widgets.Button(name="\u2039", icon="angle-left", width=40, height=30, styles=btn_style)
        btn_next = pn.widgets.Button(name="\u203a", icon="angle-right", width=40, height=30, styles=btn_style)
        btn_last = pn.widgets.Button(name="\u00bb", icon="angles-right", width=40, height=30, styles=btn_style)

        btn_first.on_click(lambda e: first_cb())
        btn_prev.on_click(lambda e: prev_cb())
        btn_next.on_click(lambda e: next_cb())
        btn_last.on_click(lambda e: last_cb())
        
        row_content = [pn.layout.HSpacer()]
        if label:
            row_content.append(pn.pane.Markdown(f"**{label}:**", align='center', margin=(0, 10)))
        
        row_content.extend([btn_first, btn_prev, btn_next, btn_last, pn.layout.HSpacer()])
        
        return pn.Row(*row_content, align='center')

    def get_controls(self):
        label = self.coord_names[0].capitalize() if len(self.coord_names) > 0 else "Slice"
        return self._make_nav_controls(
            self.first_slice, self.prev_slice, self.next_slice, self.last_slice,
            label=label
        )
