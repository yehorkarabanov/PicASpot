"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add the parent directory to the Python path
# This ensures that 'app' module can be imported correctly
project_root = Path(__file__).parent.parent.resolve()
project_root_str = str(project_root)

# Remove any conflicting paths and add our project root at the beginning
if project_root_str in sys.path:
    sys.path.remove(project_root_str)
sys.path.insert(0, project_root_str)

