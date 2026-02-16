
import holoviews as hv
import geoviews as gv
import panel as pn
import cartopy.crs as ccrs
from holoviews.operation.datashader import rasterize
from holoviews import streams

from model.FigureNode import FigureNode
from model.model_utils import PlotType
from loguru import logger

class TwoDNode(FigureNode):
    def __init__(self, id, data, title=None, field_name=None, bbox=None, 
                 plot_type=PlotType.TwoD, parent=None, cmap=None, **params):
        super().__init__(id, data, title=title, field_name=field_name,
                         bbox=bbox, plot_type=plot_type, parent=parent, cmap=cmap, **params)
        shape_str = str(data.shape) if hasattr(data, 'shape') else "Dataset (no shape)"
        logger.info(f"Created TwoDNode: id={id}, shape={shape_str}, coords={self.coord_names}")

    def create_figure(self):
        # Assume 2D data: [lat, lon]
        lats = self.data.coords[self.coord_names[-2]].values
        lons = self.data.coords[self.coord_names[-1]].values

        vdims = [hv.Dimension(self.field_name, label=self.label)]
        self.img = gv.Image((lons, lats, self.data), [self.coord_names[-1], self.coord_names[-2]], 
                            vdims=vdims, crs=ccrs.PlateCarree())

        # Project to Web Mercator BEFORE rasterizing
        projected = gv.project(self.img, projection=ccrs.GOOGLE_MERCATOR)
        
        # We use apply.opts to link cmap, clim, and cnorm parameters reactively.
        # This prevents the viewport from resetting when visual options change.
        rasterized = rasterize(projected, pixel_ratio=2).apply.opts(
            cmap=self.param.cmap,
            clim=self.param.clim,
            cnorm=self.param.cnorm,
            colorbar=True,
            responsive=True,
        )

        # Build the geo overlay using the shared helper
        self.base_plot = self._build_geo_overlay(rasterized, responsive=True)
        return self.base_plot

    def get_controls(self):
        return None
