
import holoviews as hv
import geoviews as gv
import cartopy.crs as ccrs
from holoviews.operation.datashader import rasterize

from model.FigureNode import FigureNode
from model.model_utils import PlotType
from loguru import logger

class TwoDNode(FigureNode):
    def __init__(self, id, data, title=None, field_name=None, bbox=None, 
                 plot_type=PlotType.TwoD, parent=None, cmap=None):
        super().__init__(id, data, title=title, field_name=field_name,
                         bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap)
        shape_str = str(data.shape) if hasattr(data, 'shape') else "Dataset (no shape)"
        logger.info(f"Created TwoDNode: id={id}, shape={shape_str}, coords={self.coord_names}")

    def create_figure(self):
        # Create a stream for the plot range to allow re-rasterization on zoom
        self.range_stream = hv.streams.RangeXY()
        
        # Assume 2D data: [lat, lon] or [y, x]
        lats = self.data.coords[self.coord_names[-2]].values
        lons = self.data.coords[self.coord_names[-1]].values

        # Base image
        self.img = gv.Image((lons, lats, self.data), [self.coord_names[-1], self.coord_names[-2]], crs=ccrs.PlateCarree())

        def dynamic_plot(x_range=None, y_range=None):
            # Apply rasterization
            rasterized = rasterize(self.img, x_range=x_range, y_range=y_range, dynamic=False).opts(
                cmap=self.cmap,
                colorbar=True,
                tools=['hover']
            )
            
            # Add tiles
            tiles = gv.tile_sources.OSM()
            return (tiles * rasterized).opts(
                title=self.title or self.id,
                responsive=True,
                aspect='equal'
            )

        self.dmap = hv.DynamicMap(dynamic_plot, streams=[self.range_stream])
        return self.dmap.opts(active_tools=['wheel_zoom', 'pan'])

    def get_stream_source(self):
        if not hasattr(self, 'dmap'):
            self.create_figure()
        return self.dmap
