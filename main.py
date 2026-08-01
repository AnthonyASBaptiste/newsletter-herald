import sys
import os

# Add backend directory to sys.path so imports resolve seamlessly
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.main import app

__all__ = ["app"]
