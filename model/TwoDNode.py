
import holoviews as hv
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
        colormap = self.cmap
        
        # Assume 2D data: [lat, lon] or [y, x]
        lats = self.data.coords[self.coord_names[-2]].values
        lons = self.data.coords[self.coord_names[-1]].values

        img = hv.Image((lons, lats, self.data), [self.coord_names[-1], self.coord_names[-2]])
        img.opts(
            cmap=colormap,
            title=self.title or self.id,
            tools=['hover'],
            colorbar=True,
            responsive=True,
            aspect='equal'
        )
        return img
