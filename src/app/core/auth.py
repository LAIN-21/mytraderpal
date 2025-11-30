"""Authentication utilities."""
import os
import base64
import json


def _decode_jwt_payload(token: str) -> dict:
    """
    Decode JWT token payload without verification.
    For production, this should verify the token signature.
    """
    try:
        # JWT format: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return {}
        
        # Decode payload (second part)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception:
        return {}


def get_user_id_from_event(event: dict) -> str:
    """
    Returns the user id from a verified authorizer claim when available.
    In DEV_MODE, allows overriding via X-MTP-Dev-User header.
    Supports Authorization: Bearer <token> header for JWT tokens.
    Raises PermissionError if no user can be determined.
    """
    headers = event.get('headers') or {}
    
    # 1) Dev override (check first in DEV_MODE)
    if os.getenv('DEV_MODE', 'false').lower() == 'true':
        # normalize header keys
        for k, v in headers.items():
            if k.lower() == 'x-mtp-dev-user' and v:
                return v

    # 2) Check Authorization header for Bearer token
    auth_header = None
    for k, v in headers.items():
        if k.lower() == 'authorization' and v:
            auth_header = v
            break
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        # Decode JWT token to get user ID
        payload = _decode_jwt_payload(token)
        if 'sub' in payload:
            return payload['sub']
        # Also check for 'cognito:username' or 'email' as fallback
        if 'cognito:username' in payload:
            return payload['cognito:username']
        if 'email' in payload:
            return payload['email']

    # 3) API Gateway (REST v1)
    rc = event.get('requestContext') or {}
    claims = (rc.get('authorizer') or {}).get('claims')
    if claims and 'sub' in claims:
        return claims['sub']

    # 4) API Gateway (HTTP v2)
    jwt_claims = (rc.get('authorizer') or {}).get('jwt', {}).get('claims', {})
    if 'sub' in jwt_claims:
        return jwt_claims['sub']

    # 5) No identity found
    raise PermissionError("Unauthorized")


