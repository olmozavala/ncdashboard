"""
Error Models Module

This module defines the error types used throughout the application.
It provides an enumeration of all possible error types and their descriptions.
"""

from enum import Enum

class ErrorType(Enum):
    """
    Enumeration of all possible error types in the application.
    
    Values:
        INVALID_REQUEST: Invalid request format or parameters
        INVALID_ROUTE: Requested route does not exist
        INTERNAL_ERROR: Unexpected internal server error
        
        # Dataset errors
        INVALID_DATASET: Invalid dataset identifier
        EMPTY_DATASET_DIR: No datasets found in the directory
        DATASET_NOT_FOUND: Requested dataset does not exist
        
        # Cache errors
        CACHE_NOT_FOUND: Cache directory or files not found
        CACHE_INDEX_ERROR: Error in cache index structure
        
        # Image errors
        IMAGE_NOT_FOUND: Requested image does not exist
        
        # Session errors
        SESSION_NOT_FOUND: Requested session does not exist
    """
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_ROUTE = "INVALID_ROUTE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    
    # Dataset errors
    INVALID_DATASET = "INVALID_DATASET"
    EMPTY_DATASET_DIR = "EMPTY_DATASET_DIR"
    DATASET_NOT_FOUND = "DATASET_NOT_FOUND"
    
    # Cache errors
    CACHE_NOT_FOUND = "CACHE_NOT_FOUND"
    CACHE_INDEX_ERROR = "CACHE_INDEX_ERROR"
    
    # Image errors
    IMAGE_NOT_FOUND = "IMAGE_NOT_FOUND"
    
    # Session errors
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"