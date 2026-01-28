
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
        # Assume 2D data: [lat, lon] or [y, x]
        lats = self.data.coords[self.coord_names[-2]].values
        lons = self.data.coords[self.coord_names[-1]].values

        # Use QuadMesh instead of Image because coordinates may not be perfectly evenly spaced
        # This fixes the spatial shift/misalignment highlighted by the warning
        self.img = gv.QuadMesh((lons, lats, self.data), [self.coord_names[-1], self.coord_names[-2]], crs=ccrs.PlateCarree())

        # Project to Web Mercator BEFORE rasterizing. 
        # This is the most robust way to ensure alignment with background tiles 
        # when using datashader with irregular or non-WebMercator source data.
        projected = gv.project(self.img, projection=ccrs.GOOGLE_MERCATOR)

        # Apply rasterization
        rasterized = rasterize(projected).opts(
            cmap=self.cmap,
            tools=['hover'],
            colorbar=True,
            responsive=True,
        )

        # Add tiles
        tiles = gv.tile_sources.OSM()
        return (tiles * rasterized).opts(active_tools=['wheel_zoom', 'pan'])

    def get_stream_source(self):
        if not hasattr(self, 'dmap'):
            self.create_figure()
        return self.dmap
