from pydantic import BaseModel
from typing import List, Dict

class DatasetInfoResponse(BaseModel):
    attrs: Dict
    dims: Dict
    variables_info: Dict
    lat: List
    lon: List