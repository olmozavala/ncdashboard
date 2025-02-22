from typing import TypedDict

class GenerateImageRequest(TypedDict):
    dataset: str
    time_index: int
    depth_index: int
    variable: str
    
