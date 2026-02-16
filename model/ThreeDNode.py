import holoviews as hv
import geoviews as gv
import panel as pn
import cartopy.crs as ccrs
from holoviews.operation.datashader import rasterize
from holoviews import streams
from loguru import logger

from model.FigureNode import FigureNode
from model.AnimationNode import AnimationNode
from model.model_utils import PlotType, Resolutions, get_all_coords

class ThreeDNode(FigureNode):
    def __init__(self, id, data, third_coord_idx=0, plot_type=PlotType.ThreeD, 
                 title=None, field_name=None, bbox=None, parent=None, cmap=None, **params):

        super().__init__(id, data, title=title, field_name=field_name, 
                         bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap, **params)

        self.third_coord_idx = third_coord_idx
        logger.info(f"Created ThreeDNode: id={id}, shape={data.shape}, coords={self.coord_names}")
        self.third_coord_name = data.coords[self.coord_names[0]].name
        
        # Stream for dynamic updates (index changes)
        self.update_stream = hv.streams.Counter()
        # Stream for capturing viewport ranges
        self.range_stream = hv.streams.RangeXY()

    def _render_plot(self, counter=0, **kwargs):
        data = self.data
        if self.plot_type == PlotType.ThreeD:
            data = self.data[self.third_coord_idx, :, :]

        lats = data.coords[self.coord_names[-2]].values
        lons = data.coords[self.coord_names[-1]].values

        title = f'{self.title} at {self.coord_names[0].capitalize()} {self.third_coord_idx}'

        vdims = [hv.Dimension(self.field_name, label=self.label)]
        img = gv.Image((lons, lats, data.values), [self.coord_names[-1], self.coord_names[-2]], 
                       vdims=vdims, crs=ccrs.PlateCarree())
        return img.opts(title=title)

    def create_figure(self):
        # We only put index and range streams in the DynamicMap.
        # This ensures that data only re-reads when the slice index changes.
        # We do NOT include cmap/clim stream here to avoid zoom resets.
        self.dmap = hv.DynamicMap(self._render_plot, 
                                  streams=[self.update_stream, self.range_stream])
        
        # We link cmap, clim, and cnorm using .apply.opts() on the rasterized output.
        # This keeps the Bokeh plot object stable while allowing visual updates.
        rasterized = rasterize(self.dmap, width=800, pixel_ratio=2).apply.opts(
            cmap=self.param.cmap,
            clim=self.param.clim,
            cnorm=self.param.cnorm,
            colorbar=True,
            responsive=True,
            aspect='equal'
        )
        
        self.range_stream.source = rasterized

        # Build the geo overlay using the shared helper
        return self._build_geo_overlay(rasterized, responsive=True, aspect='equal')

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

    def _animate_callback(self, animation_coord, data=None):
        if self.add_node_callback is None:
            logger.warning("No add_node_callback found for animation callback")
            return

        x_range = self.range_stream.x_range
        y_range = self.range_stream.y_range
        
        logger.info(f"Starting animation for {animation_coord} in range X:{x_range} Y:{y_range}")
        data_to_use = data if data is not None else self.data

        if self.id_generator_callback:
            node_id = self.id_generator_callback(f"{self.id}_anim")
        else:
            node_id = f"{self.id}_anim"

        anim_node = AnimationNode(node_id, data_to_use, animation_coord, Resolutions.HIGH.value, 
                                  title=self.title, field_name=self.field_name, 
                                  bbox=self.bbox, parent=self, cmap=self.cmap,
                                  x_range=x_range, y_range=y_range)
        
        self.add_node_callback(anim_node)

    def _make_nav_controls(self, first_cb, prev_cb, next_cb, last_cb, label=None, anim_coord=None):
        btn_style = {'margin': '0px 2px'}
        btn_first = pn.widgets.Button(name="\u00ab", icon="angles-left", width=40, height=30, styles=btn_style)
        btn_prev = pn.widgets.Button(name="\u2039", icon="angle-left", width=40, height=30, styles=btn_style)
        btn_next = pn.widgets.Button(name="\u203a", icon="angle-right", width=40, height=30, styles=btn_style)
        btn_last = pn.widgets.Button(name="\u00bb", icon="angles-right", width=40, height=30, styles=btn_style)
        btn_anim = pn.widgets.Button(name="Animate", icon="film", button_type="primary", height=30, styles=btn_style)

        btn_first.on_click(lambda e: first_cb())
        btn_prev.on_click(lambda e: prev_cb())
        btn_next.on_click(lambda e: next_cb())
        btn_last.on_click(lambda e: last_cb())
        
        if anim_coord:
            btn_anim.on_click(lambda e: self._animate_callback(anim_coord))
        else:
             btn_anim.disabled = True
        
        row_content = [pn.layout.HSpacer()]
        if label:
            row_content.append(pn.pane.Markdown(f"**{label}:**", align='center', margin=(0, 10)))
        
        row_content.extend([btn_first, btn_prev, btn_next, btn_last, btn_anim, pn.layout.HSpacer()])
        return pn.Row(*row_content, align='center')

    def get_controls(self):
        label = self.coord_names[0].capitalize() if len(self.coord_names) > 0 else "Slice"
        return self._make_nav_controls(
            self.first_slice, self.prev_slice, self.next_slice, self.last_slice,
            label=label,
            anim_coord=self.coord_names[0]
        )
