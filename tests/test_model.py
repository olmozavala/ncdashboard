import pytest
import xarray as xr
import numpy as np
import holoviews as hv
import geoviews as gv
from unittest.mock import patch
from model.TwoDNode import TwoDNode
from model.ThreeDNode import ThreeDNode
from model.FourDNode import FourDNode
from model.model_utils import PlotType

# Initialize holoviews for testing
hv.extension('bokeh')

@pytest.fixture
def mock_2d_data():
    data = np.random.rand(10, 10)
    coords = {'lat': np.arange(10), 'lon': np.arange(10)}
    da = xr.DataArray(data, coords=coords, dims=('lat', 'lon'), name='temp')
    da.attrs['long_name'] = 'Temperature'
    da.attrs['units'] = 'C'
    return da

@pytest.fixture
def mock_3d_data():
    data = np.random.rand(5, 10, 10)
    coords = {'time': np.arange(5), 'lat': np.arange(10), 'lon': np.arange(10)}
    da = xr.DataArray(data, coords=coords, dims=('time', 'lat', 'lon'), name='temp')
    da.attrs['long_name'] = 'Temperature'
    da.attrs['units'] = 'C'
    return da

@pytest.fixture
def mock_4d_data():
    data = np.random.rand(5, 2, 10, 10)
    coords = {'time': np.arange(5), 'depth': np.arange(2), 'lat': np.arange(10), 'lon': np.arange(10)}
    da = xr.DataArray(data, coords=coords, dims=('time', 'depth', 'lat', 'lon'), name='temp')
    da.attrs['long_name'] = 'Temperature'
    da.attrs['units'] = 'C'
    return da

def test_twod_node_init(mock_2d_data):
    node = TwoDNode("test_2d", mock_2d_data, field_name='temp')
    assert node.id == "test_2d"
    assert node.plot_type == PlotType.TwoD
    assert node.cnorm == 'linear'
    assert node.cmap is not None

@patch('geoviews.project')
@patch('geoviews.tile_sources.OSM')
def test_twod_node_create_figure(mock_osm, mock_project, mock_2d_data):
    # Mock OSM return to be an Element that supports * operator
    mock_osm.return_value = hv.Curve([]) 
    mock_project.return_value = hv.Image(np.random.rand(10,10)) 

    node = TwoDNode("test_2d", mock_2d_data, field_name='temp')
    fig = node.create_figure()
    assert fig is not None

def test_threed_node_init(mock_3d_data):
    node = ThreeDNode("test_3d", mock_3d_data, third_coord_idx=0)
    assert node.id == "test_3d"
    assert node.plot_type == PlotType.ThreeD
    assert node.third_coord_idx == 0

def test_threed_node_reactive_params(mock_3d_data):
    node = ThreeDNode("test_3d", mock_3d_data)
    # Ensure it is parameterized
    assert hasattr(node, 'param')
    assert 'cmap' in node.param
    assert 'cnorm' in node.param
    
    # Check default
    assert node.cnorm == 'linear'
    
    # Update param
    node.cnorm = 'log'
    assert node.cnorm == 'log'

def test_fourd_node_init(mock_4d_data):
    node = FourDNode("test_4d", mock_4d_data, time_idx=0, depth_idx=0)
    assert node.id == "test_4d"
    assert node.plot_type == PlotType.FourD
    assert node.depth_idx == 0

@patch('geoviews.tile_sources.OSM')
def test_fourd_node_create_figure(mock_osm, mock_4d_data):
    mock_osm.return_value = hv.Curve([])
    node = FourDNode("test_4d", mock_4d_data, time_idx=0, depth_idx=0, field_name='temp')
    fig = node.create_figure()
    assert fig is not None
