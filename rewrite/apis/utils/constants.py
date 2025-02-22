import os

# Datasets
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../../test_data')

# Cache
CACHE_DIR = os.path.join(os.path.dirname(__file__), '../.nc_cache')
CACHE_INDEX_FILE = os.path.join(CACHE_DIR, 'index.json')