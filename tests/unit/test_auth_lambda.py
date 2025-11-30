import sys
import os
from unittest.mock import patch
import pytest

# Add src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app.core.auth import get_user_id_from_event


class TestAuthLambda:
    def test_dev_mode_with_valid_header(self):
        """Test dev mode with valid X-MTP-Dev-User header"""
        event = {
            'headers': {'X-MTP-Dev-User': 'test-user-123'}
        }
        
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            result = get_user_id_from_event(event)
            assert result == 'test-user-123'
    
    def test_dev_mode_with_case_insensitive_header(self):
        """Test dev mode with case insensitive header"""
        event = {
            'headers': {'x-mtp-dev-user': 'test-user-456'}
        }
        
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            result = get_user_id_from_event(event)
            assert result == 'test-user-456'
    
    def test_dev_mode_with_empty_header(self):
        """Test dev mode with empty dev header falls back to JWT"""
        event = {
            'headers': {'X-MTP-Dev-User': ''},
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'jwt-user-123'}
                }
            }
        }
        
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            result = get_user_id_from_event(event)
            assert result == 'jwt-user-123'
    
    def test_dev_mode_without_header(self):
        """Test dev mode without dev header falls back to JWT"""
        event = {
            'headers': {},
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'jwt-user-456'}
                }
            }
        }
        
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            result = get_user_id_from_event(event)
            assert result == 'jwt-user-456'
    
    def test_production_mode_rest_api_v1(self):
        """Test production mode with REST API v1 format"""
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'prod-user-123'}
                }
            }
        }
        
        with patch.dict(os.environ, {'DEV_MODE': 'false'}):
            result = get_user_id_from_event(event)
            assert result == 'prod-user-123'
    
    def test_production_mode_http_api_v2(self):
        """Test production mode with HTTP API v2 format"""
        event = {
            'requestContext': {
                'authorizer': {
                    'jwt': {
                        'claims': {'sub': 'v2-user-123'}
                    }
                }
            }
        }
        
        with patch.dict(os.environ, {'DEV_MODE': 'false'}):
            result = get_user_id_from_event(event)
            assert result == 'v2-user-123'
    
    def test_no_identity_found_raises_permission_error(self):
        """Test that PermissionError is raised when no identity is found"""
        event = {
            'headers': {},
            'requestContext': {}
        }
        
        with patch.dict(os.environ, {'DEV_MODE': 'false'}):
            with pytest.raises(PermissionError, match="Unauthorized"):
                get_user_id_from_event(event)
    
    def test_missing_request_context(self):
        """Test handling of missing requestContext"""
        event = {
            'headers': {}
        }
        
        with patch.dict(os.environ, {'DEV_MODE': 'false'}):
            with pytest.raises(PermissionError, match="Unauthorized"):
                get_user_id_from_event(event)
    
    def test_missing_headers(self):
        """Test handling of missing headers"""
        event = {}
        
        with patch.dict(os.environ, {'DEV_MODE': 'true'}):
            with pytest.raises(PermissionError, match="Unauthorized"):
                get_user_id_from_event(event)
