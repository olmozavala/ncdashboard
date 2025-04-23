"""
Database Models Module

This module defines the data models for the application's database structure.
It provides type definitions for datasets and the main database structure.
"""

from typing import TypedDict
from .session import Session

# TODO: Find better place for dataset type
class Dataset(TypedDict):
    """
    A dataset object representing a data source in the application.
    
    Attributes:
        id (str): Unique identifier for the dataset
        name (str): Human-readable name of the dataset
        path (str): File system path to the dataset
    """
    id: str
    name: str
    path: str
    

class NC_DataBaseType(TypedDict):
    """
    The main database structure containing all application data.
    
    Attributes:
        datasets (list[Dataset]): List of available datasets
        sessions (list[Session]): List of active sessions
    """
    datasets: list[Dataset]
    sessions: list[Session]
    