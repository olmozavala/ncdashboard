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
    """
    Intelligently identifies time, depth, latitude, and longitude coordinates.
    Prioritizes coordinates that match the dimensions of the input DataArray.
    """
    lats = xr.DataArray(np.empty(0))
    lons = xr.DataArray(np.empty(0))
    times = xr.DataArray(np.empty(0))
    depth = xr.DataArray(np.empty(0))

    data_dims = set(data.dims)

    def is_lat(v):
        name = v.name.lower()
        return name in ['lat', 'latitude', 'xlat', 'nav_lat', 'yc'] or 'lat' in name
    
    def is_lon(v):
        name = v.name.lower()
        return name in ['lon', 'longitude', 'xlong', 'nav_lon', 'xc'] or 'lon' in name

    def is_time(v):
        name = v.name.lower()
        return name in ['time', 'xtime', 'times', 't']
    
    def is_depth(v):
        name = v.name.lower()
        return name in ['depth', 'z', 'lev', 'level', 'bottom_top', 'pressure'] or 'depth' in name

    # 1. Filter coordinates that belong to this variable
    # We prioritize those whose dimensions are a SUBSET of the variable's dimensions.
    relevant_coords = [data.coords[c] for c in data.coords if set(data.coords[c].dims).issubset(data_dims)]
    
    # 2. Assign by name matching from relevant coords
    for c in relevant_coords:
        if is_lat(c) and lats.size == 0: lats = c
        elif is_lon(c) and lons.size == 0: lons = c
        elif is_time(c) and times.size == 0: times = c
        elif is_depth(c) and depth.size == 0: depth = c

    # 3. Fallbacks based on dimension position if not found by name
    dims = list(data.dims)
    if lats.size == 0 and len(dims) >= 2:
        lats = data[dims[-2]]
    if lons.size == 0 and len(dims) >= 1:
        lons = data[dims[-1]]

    if times.size == 0 and len(dims) >= 3:
        times = data[dims[0]]
    if depth.size == 0 and len(dims) == 4:
        depth = data[dims[1]]

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