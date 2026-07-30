"""
dependencies.py

Shared FastAPI dependencies used across multiple routers.
Currently re-exports get_db for convenience; extend this file with
things like auth/current-user dependencies in future phases.
"""

from app.database import get_db

__all__ = ["get_db"]
