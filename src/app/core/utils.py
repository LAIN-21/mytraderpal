"""General utility functions."""
from datetime import datetime, timezone
from typing import Optional


def now_iso() -> str:
    """Get current UTC time as ISO format string."""
    return datetime.now(timezone.utc).isoformat()


def generate_id(prefix: str) -> str:
    """
    Generate a unique ID with a prefix.
    Uses ULID if available, otherwise falls back to UUID4.
    """
    try:
        import ulid
        return f"{prefix}-{ulid.new()}"
    except ImportError:
        import uuid
        return f"{prefix}-{uuid.uuid4()}"


