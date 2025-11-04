"""
Test configuration for integration tests in app/test directory.
Reuses the fixtures from backend/tests/conftest.py
"""
import sys
from pathlib import Path

# Add backend directory to path to import fixtures
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Import all fixtures from the main conftest
from tests.conftest import *  # noqa: F401, F403
