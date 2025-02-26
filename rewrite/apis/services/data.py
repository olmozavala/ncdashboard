import os
from uuid import uuid4
from datetime import datetime, timezone
from utils.constants import DATA_DIR 
from models import Dataset
from services.db import nc_db

def get_available_datasets():
    data_files = os.listdir(DATA_DIR)
        
    for file in data_files:
        dataset = nc_db.get_dataset_by_name(file)
        if not dataset:
            dataset = Dataset()
            dataset["id"] = str(uuid4())
            dataset["name"] = file
            dataset["path"] = os.path.join(DATA_DIR, file)
            nc_db.add_dataset(dataset)
    
    return nc_db.db['datasets']