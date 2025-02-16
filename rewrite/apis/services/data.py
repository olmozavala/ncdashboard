import os
from utils.constants import DATA_DIR 

def get_available_datasets():
    data_files = os.listdir(DATA_DIR)
    return data_files