from enum import Enum
import numpy as np
from collections import deque
import xarray as xr


def select_anim_data(data, coord_idx, plot_type) -> xr.DataArray:
    data_anim = data
    if plot_type == PlotType.FourD_Animation:
        # TODO this needs to be improved, completely hardcoded
        if coord_idx == 0:
            data_anim = data[:, 0,:,:].squeeze()
        elif coord_idx == 1:
            data_anim = data[0, :,:,:].squeeze()
        else:
            # Log an error and raise an exception that the animation dimension is not the first or second
            error ="Error: animation dimension is not the first or second" 
            print(error)
            raise Exception(error)
    return data_anim

def get_all_coords(data):
    '''
    This method returns the coordinates for a given data 
    '''
    coords =  list(data.coords.keys())
    # Assume the last 2 are the spatial coordinates 
    lats = xr.DataArray(np.empty((0, 0)))
    lons = xr.DataArray(np.empty((0, 0)))
    times = xr.DataArray(np.empty((0, 0)))
    zaxis = xr.DataArray(np.empty((0, 0)))

    if len(coords) == 1: # In this case we assume we have time, z, lat, lon
        lats = data[coords[0]]

    if len(coords) >= 2: # In this case we assume we have time, z, lat, lon
        lats = data[coords[-2]]
        lons = data[coords[-1]]

    # TODO this should be something smarter, based on the names of the coordinates
    if len(coords) >= 3: # In this case we assume we have time, z, lat, lon
        times = data[coords[0]]

    if len(coords) == 4: # In this case we assume we have time, z, lat, lon
        zaxis = data[coords[1]]

    return times, zaxis, lats, lons

class PlotType(Enum):
    OneD = 1
    TwoD = 2
    ThreeD = 3
    FourD = 4
    OneD_Animation = 15
    TwoD_Animation = 16
    ThreeD_Animation = 17
    FourD_Animation = 18

    def is_animation(self):
        return self.value >= 10

    def can_request_animation(self):
        return self.value in {3, 4}