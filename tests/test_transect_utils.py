"""
Tests for transect utilities.
"""

import pytest
import numpy as np
import xarray as xr

from model.transect_utils import compute_path_points, extract_transect, get_transect_title


class TestComputePathPoints:
    """Tests for compute_path_points function."""
    
    def test_simple_horizontal_line(self):
        """Test path points along a horizontal line."""
        xs = np.array([0, 10])
        ys = np.array([5, 5])
        
        lons, lats, distances = compute_path_points(xs, ys, num_points=11)
        
        assert len(lons) == 11
        assert len(lats) == 11
        assert len(distances) == 11
        
        # Check first and last points
        assert lons[0] == 0
        assert lons[-1] == 10
        assert lats[0] == 5
        assert lats[-1] == 5
        
        # Check distances
        assert distances[0] == 0
        assert distances[-1] == pytest.approx(10, rel=1e-6)
    
    def test_diagonal_line(self):
        """Test path points along a diagonal line."""
        xs = np.array([0, 3])
        ys = np.array([0, 4])
        
        lons, lats, distances = compute_path_points(xs, ys, num_points=6)
        
        # Total distance should be 5 (3-4-5 triangle)
        assert distances[-1] == pytest.approx(5, rel=1e-6)
    
    def test_multipoint_path(self):
        """Test path with multiple vertices."""
        xs = np.array([0, 5, 5])
        ys = np.array([0, 0, 5])
        
        lons, lats, distances = compute_path_points(xs, ys, num_points=11)
        
        # Total distance should be 10 (5 + 5)
        assert distances[-1] == pytest.approx(10, rel=1e-6)
    
    def test_minimum_points_error(self):
        """Test that single point path raises error."""
        xs = np.array([5])
        ys = np.array([5])
        
        with pytest.raises(ValueError):
            compute_path_points(xs, ys)
    
    def test_zero_length_path_error(self):
        """Test that zero-length path raises error."""
        xs = np.array([5, 5])
        ys = np.array([5, 5])
        
        with pytest.raises(ValueError):
            compute_path_points(xs, ys)


class TestExtractTransect:
    """Tests for extract_transect function."""
    
    @pytest.fixture
    def data_2d(self):
        """Create sample 2D data."""
        lats = np.linspace(-10, 10, 21)
        lons = np.linspace(-20, 20, 41)
        values = np.random.rand(21, 41)
        
        return xr.DataArray(
            values,
            dims=['lat', 'lon'],
            coords={'lat': lats, 'lon': lons},
            attrs={'long_name': 'Test Variable', 'units': 'm/s'}
        )
    
    @pytest.fixture
    def data_3d(self):
        """Create sample 3D data (time, lat, lon)."""
        times = np.arange(5)
        lats = np.linspace(-10, 10, 21)
        lons = np.linspace(-20, 20, 41)
        values = np.random.rand(5, 21, 41)
        
        return xr.DataArray(
            values,
            dims=['time', 'lat', 'lon'],
            coords={'time': times, 'lat': lats, 'lon': lons},
            attrs={'long_name': 'Test 3D', 'units': 'K'}
        )
    
    @pytest.fixture
    def data_4d(self):
        """Create sample 4D data (time, depth, lat, lon)."""
        times = np.arange(3)
        depths = np.array([0, 10, 50, 100])
        lats = np.linspace(-10, 10, 21)
        lons = np.linspace(-20, 20, 41)
        values = np.random.rand(3, 4, 21, 41)
        
        return xr.DataArray(
            values,
            dims=['time', 'depth', 'lat', 'lon'],
            coords={'time': times, 'depth': depths, 'lat': lats, 'lon': lons},
            attrs={'long_name': 'Test 4D', 'units': 'psu'}
        )
    
    def test_transect_2d_to_1d(self, data_2d):
        """Test transect from 2D data produces 1D output."""
        path_xs = [-15, 15]
        path_ys = [0, 0]
        
        result = extract_transect(data_2d, path_xs, path_ys, num_points=50)
        
        assert len(result.dims) == 1
        assert 'distance' in result.dims
        assert len(result.coords['distance']) == 50
    
    def test_transect_3d_to_2d(self, data_3d):
        """Test transect from 3D data produces 2D output."""
        path_xs = [-15, 15]
        path_ys = [0, 0]
        
        result = extract_transect(data_3d, path_xs, path_ys, num_points=30)
        
        assert len(result.dims) == 2
        assert 'distance' in result.dims
        assert 'time' in result.dims
        assert result.shape == (5, 30)  # (time, distance)
    
    def test_transect_4d_to_3d(self, data_4d):
        """Test transect from 4D data produces 3D output."""
        path_xs = [-15, 15]
        path_ys = [0, 0]
        
        result = extract_transect(data_4d, path_xs, path_ys, num_points=25)
        
        assert len(result.dims) == 3
        assert 'distance' in result.dims
        assert 'time' in result.dims
        assert 'depth' in result.dims
        assert result.shape == (3, 4, 25)  # (time, depth, distance)
    
    def test_transect_preserves_attrs(self, data_2d):
        """Test that transect preserves data attributes."""
        path_xs = [-15, 15]
        path_ys = [0, 0]
        
        result = extract_transect(data_2d, path_xs, path_ys)
        
        assert result.attrs.get('long_name') == 'Test Variable'
        assert result.attrs.get('units') == 'm/s'
        assert 'transect_path_xs' in result.attrs
        assert 'transect_path_ys' in result.attrs


class TestGetTransectTitle:
    """Tests for get_transect_title function."""
    
    def test_title_format(self):
        """Test title is formatted correctly."""
        title = get_transect_title("Sea Surface Temperature", (-5, 10), (5, -10))
        
        assert "Sea Surface Temperature" in title
        assert "Transect" in title
        assert "-5.00" in title
        assert "10.00" in title


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
