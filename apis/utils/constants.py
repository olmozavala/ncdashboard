"""
Constants Module

This module defines global constants used throughout the application.
It includes paths for data storage, cache directories, and configuration files.
"""

import os

# Dataset configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../test_data')
# Alternative data directory (commented out)
# DATA_DIR = "/research/osz09/DATA/anand"

# Cache configuration
CACHE_DIR = os.path.join(os.path.dirname(__file__), '../.nc_cache')
CACHE_INDEX_FILE = os.path.join(CACHE_DIR, 'index.json')