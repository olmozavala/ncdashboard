"""
+---------------------------------------------------------------+
|                         FastAPI Routers                       |
+---------------------------------------------------------------+
| WARNING:                                                      |
| - Any router imported in this file will be automatically      |
|   registered in the main FastAPI application.                 |
| - Ensure that routers are properly defined in their respective|
|   modules and working correctly before adding them here.      |
+---------------------------------------------------------------+
"""

from .data import router as data_router
from .image import router as image_router