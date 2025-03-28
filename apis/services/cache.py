import os
import json
from uuid import uuid4 
from datetime import datetime, timezone
import xarray as xr
from utils.constants import CACHE_DIR, DATA_DIR, CACHE_INDEX_FILE
from models import ErrorType, CacheIndex, CachedDataset 

from .image import generate_image

def check_cache():
    try:
        if os.path.exists(CACHE_DIR):
            cache_index_path = CACHE_INDEX_FILE
            if os.path.exists(cache_index_path):
                with open(cache_index_path, 'r') as cache_file:
                    cache_data: CacheIndex = json.load(cache_file)
                    return cache_data
            else:
                return ErrorType.CACHE_INDEX_ERROR.value
        else:
            return ErrorType.CACHE_NOT_FOUND.value
    except Exception as e:
        return ErrorType.INTERNAL_ERROR.value



def generate_cache_files(dataset_name: str = None):
    data_files = os.listdir(DATA_DIR)
    
    index:CacheIndex = {
        'cache': []
    }
    for file in data_files:
        dataset_metadata: CachedDataset = {
            'id': str(uuid4()), 
            "created_at": datetime.now(timezone.utc),
            'description': "",
            "name": file,
            'images': []
        }
        
        index['cache'].append(dataset_metadata)
    
    # Create the cache dir
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    for d in index['cache']:
        dataset_path = os.path.join(CACHE_DIR, d['id'])
        os.makedirs(dataset_path, exist_ok=True)
        
        data = xr.open_dataset(os.path.join(DATA_DIR, d['name']), decode_times=False)
        
        for t in range(1):#range(data.dims['time']):
            for z in range(1): #range(data.dims['depth']):
                image_index = {
                    'id': str(uuid4()),
                    'dataset_id': d['id'],
                    'variable': f'water_u&t={t}&z={z}',
                    'file_path': os.path.join(dataset_path, f"{t}_{z}.jpeg")
                }
                image_data = generate_image(d['name'], t, z, data=data)
                image_path = os.path.join(dataset_path, f"{image_index['id']}.jpeg")
                with open(image_path, 'wb') as image_file:
                    image_file.write(image_data)
                d['images'].append(image_index)
    
        
    # Write the index file
    with open(CACHE_INDEX_FILE, 'w') as cache_file:
        json.dump(index, cache_file, indent=4, default=str)
    
    return index