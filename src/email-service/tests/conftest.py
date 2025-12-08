"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add the parent directory to the Python path
# This ensures that 'app' module can be imported correctly
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

