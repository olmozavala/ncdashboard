from enum import Enum
import numpy as np
from collections import deque
import xarray as xr

def select_spatial_location(data, lat, lon, coord_names) -> xr.DataArray:
    '''
    This method returns the data for a given lat and lon
    '''

    # TOOD We are assuming that the last two coords are always lat and lon
    subset_data = data.sel({coord_names[-2]:lat, coord_names[-1]:lon}, method="nearest") 

    return subset_data

def select_profile(data, profile_coord, coord_names) -> xr.DataArray:
    '''
    This method returns the data for a given profile
    '''
    # Let's fix all dimensions at their 0th index except the profile_coord
    indexing_dict = {dim: 0 for dim in coord_names if dim != profile_coord}  
    coordinate = data.coords[profile_coord]

    # Now, you can index your array using this dictionary
    # This will give you a 1D array along the last profile dimension
    profile = data.isel(indexing_dict)

    # Get the non nan indexes from the profile and clip the coordinate
    non_nan_indexes = np.where(~np.isnan(profile))[0]
    profile = profile[non_nan_indexes]
    coordinate = coordinate[non_nan_indexes]

    return profile


def select_anim_data(data, third_coord_idx, plot_type) -> xr.DataArray:
    data_anim = data
    if plot_type == PlotType.FourD_Animation:
        # TODO this needs to be improved, completely hardcoded
        if third_coord_idx == 0:
            data_anim = data[:, 0,:,:].squeeze()
        elif third_coord_idx == 1:
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
    # Use dims instead of coords.keys() to ensure we match the data axes
    coords = list(data.dims)
    lats = xr.DataArray(np.empty((0, 0)))
    lons = xr.DataArray(np.empty((0, 0)))
    times = xr.DataArray(np.empty((0, 0)))
    depth = xr.DataArray(np.empty((0, 0)))

    if len(coords) == 1: # In this case we assume we have time, z, lat, lon
        lons = data[coords[0]]

    if len(coords) >= 2: # In this case we assume we have time, z, lat, lon
        lats = data[coords[-2]]
        lons = data[coords[-1]]

    # TODO this should be something smarter, based on the names of the coordinates
    if len(coords) >= 3: # In this case we assume we have time, z, lat, lon
        times = data[coords[0]]

    if len(coords) == 4: # In this case we assume we have time, z, lat, lon
        depth = data[coords[1]]

    return times, depth, lats, lons

def print_tree(node, level=0, prefix="Root: "):
    print(" " * (level * 4) + prefix + str(node.id))
    for i, child in enumerate(node.get_children()):
        if i == len(node.get_children()) - 1:
            new_prefix = "└── "
        else:
            new_prefix = "├── "
        print_tree(child, level + 1, prefix=new_prefix)

class PlotType(Enum):
    OneD = 1
    TwoD = 2
    ThreeD = 3
    FourD = 4
    Profile = 5
    OneD_Animation = 15
    TwoD_Animation = 16
    ThreeD_Animation = 17
    FourD_Animation = 18

    def is_animation(self):
        return self.value >= 10

    def can_request_animation(self):
        return self.value in {3, 4}

class Resolutions(Enum):
    LOW = "high"
    MEDIUM = "medium"
    HIGH = "low"