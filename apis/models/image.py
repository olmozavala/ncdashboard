from typing import TypedDict, Optional

class Image(TypedDict):
    id: str
    dataset_id: str
    variable: str
    file_path: str
    created_at: str
    color_map: Optional[str]