from typing import TypedDict
from .image import Image 



class CachedDataset(TypedDict):
    id: str
    name: str
    description: str
    created_at: str
    images: list[Image]
        
    
class CacheIndex(TypedDict):
    cache: list[CachedDataset]