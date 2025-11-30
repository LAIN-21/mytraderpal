"""Test import paths helper - ensures all imports work with new structure."""
import sys
import os

# Add src directory to Python path for tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

# Verify imports work
try:
    from app.main import handler
    from app.api.router import route_request
    from app.core.auth import get_user_id_from_event
    from app.core.response import success_response, error_response
    from app.repositories.dynamodb import db
    from app.services.note_service import note_service
    from app.services.strategy_service import strategy_service
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    raise


