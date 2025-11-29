"""Response utilities for Lambda handler."""
import json
from decimal import Decimal
from typing import Dict, Any, Optional


def decimal_default(obj: Any) -> Any:
    """JSON serializer for Decimal objects."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def get_origin(event: Dict[str, Any]) -> str:
    """Extract origin from event headers."""
    headers = event.get('headers') or {}
    # Handle case-insensitive header keys
    origin = headers.get('origin') or headers.get('Origin') or '*'
    return origin


def cors_headers(origin: Optional[str] = None) -> Dict[str, str]:
    """Generate CORS headers."""
    if origin is None or origin == '*':
        origin = '*'
    else:
        # Allow localhost for development
        if 'localhost' in origin or '127.0.0.1' in origin:
            pass  # Keep the origin as-is
        # For production, you might want to validate against allowed origins
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
    }
    
    # Add credentials header if origin is not wildcard
    if origin != '*':
        headers['Access-Control-Allow-Credentials'] = 'true'
    
    return headers


def success_response(
    body: Dict[str, Any],
    origin: Optional[str] = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """Create a successful HTTP response."""
    return {
        'statusCode': status_code,
        'headers': cors_headers(origin),
        'body': json.dumps(body, default=decimal_default)
    }


def error_response(
    status_code: int,
    message: str,
    origin: Optional[str] = None
) -> Dict[str, Any]:
    """Create an error HTTP response."""
    return {
        'statusCode': status_code,
        'headers': cors_headers(origin),
        'body': json.dumps({'message': message})
    }

