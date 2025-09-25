import os
import json
from typing import Optional
from fastapi import HTTPException, Request
from jose import jwt, JWTError


def get_user_id_from_request(request: Request) -> str:
    """Extract user ID from JWT token or dev mode header."""
    
    # Dev mode check
    dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
    if dev_mode:
        dev_user = request.headers.get('X-MTP-Dev-User')
        if dev_user == 'dev':
            return 'dev-user'
    
    # Extract JWT from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Missing or invalid authorization header')
    
    token = auth_header.split(' ')[1]
    
    try:
        # Decode JWT token (in production, you'd verify the signature)
        payload = jwt.get_unverified_claims(token)
        user_id = payload.get('sub')
        
        if not user_id:
            raise HTTPException(status_code=401, detail='Invalid token: missing sub claim')
        
        return user_id
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f'Invalid token: {str(e)}')
