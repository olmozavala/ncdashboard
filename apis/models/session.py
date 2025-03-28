from typing import TypedDict, Optional
from .image import Image
from .cache import CachedDataset

class SessionParams(TypedDict):
    colorspace: str
    variable: str

class Session(TypedDict):
    id: str
    parent_id: Optional[str]
    created_at: str
    dataset_id: str
    params: list[SessionParams]
    cache: Optional[CachedDataset]