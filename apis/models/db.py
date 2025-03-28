from typing import TypedDict
from .session import Session

# TODO: Find better place for dataset type
class Dataset(TypedDict):
    id: str
    name: str
    path: str
    

class NC_DataBaseType(TypedDict):
    datasets: list[Dataset]
    sessions: list[Session]
    