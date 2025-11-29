"""Authentication utilities."""
import os


def get_user_id_from_event(event: dict) -> str:
    """
    Returns the user id from a verified authorizer claim when available.
    In DEV_MODE, allows overriding via X-MTP-Dev-User header.
    Raises PermissionError if no user can be determined.
    """
    # 1) Dev override
    if os.getenv('DEV_MODE', 'false').lower() == 'true':
        headers = event.get('headers') or {}
        # normalize header keys
        for k, v in headers.items():
            if k.lower() == 'x-mtp-dev-user' and v:
                return v

    # 2) API Gateway (REST v1)
    rc = event.get('requestContext') or {}
    claims = (rc.get('authorizer') or {}).get('claims')
    if claims and 'sub' in claims:
        return claims['sub']

    # 3) API Gateway (HTTP v2)
    jwt_claims = (rc.get('authorizer') or {}).get('jwt', {}).get('claims', {})
    if 'sub' in jwt_claims:
        return jwt_claims['sub']

    # 4) No identity found
    raise PermissionError("Unauthorized")

