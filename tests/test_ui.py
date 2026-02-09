import pytest
from unittest.mock import MagicMock, patch
import xarray as xr
from model.dashboard import Dashboard

@pytest.fixture
def mock_mfdataset():
    data = MagicMock(spec=xr.Dataset)
    data.variables = ['temp', 'salt', 'lat', 'lon']
    
    # Mock shapes
    temp = MagicMock()
    temp.shape = (10, 10, 10, 10)
    data.__getitem__.side_effect = lambda key: temp if key == 'temp' else MagicMock(shape=(10, 10))
    
    return data

@patch('xarray.open_mfdataset')
def test_dashboard_init(mock_open, mock_mfdataset):
    mock_open.return_value = mock_mfdataset
    dashboard = Dashboard(path="dummy_path", regex="dummy_regex")
    
    assert dashboard.path == "dummy_path"
    assert dashboard.regex == "dummy_regex"
    assert 'temp' in dashboard.four_d

@patch('xarray.open_mfdataset')
def test_dashboard_get_field_names(mock_open, mock_mfdataset):
    mock_dataset = MagicMock(spec=xr.Dataset)
    mock_dataset.variables = ['temp4d', 'temp3d']
    
    var4d = MagicMock()
    var4d.shape = (1, 2, 3, 4)
    var4d.dims = ('t', 'z', 'y', 'x')
    var4d.long_name = 'temp4d_long'
    
    var3d = MagicMock()
    var3d.shape = (1, 2, 3)
    var3d.dims = ('t', 'y', 'x')
    var3d.long_name = 'temp3d_long'
    
    def getitem(key):
        if key == 'temp4d': return var4d
        if key == 'temp3d': return var3d
        return MagicMock()
    
    mock_dataset.__getitem__.side_effect = getitem
    mock_open.return_value = mock_dataset
    
    # Dashboard init processes variables
    dash = Dashboard("p", "r")
    
    fields_3d = dash.get_field_names('3D')
    assert len(fields_3d) == 1
    assert fields_3d[0][0] == 'temp3d_long' # Name from long_name
