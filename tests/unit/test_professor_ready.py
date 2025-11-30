"""
Professor-Ready Test Suite
==========================

This test suite is designed to work completely offline without any AWS dependencies.
All tests use proper mocking to ensure they work on any machine without AWS access.

To run: python -m pytest tests/unit/test_professor_ready.py -v
"""

import sys
import os
import json
from unittest.mock import patch, MagicMock
import pytest

# Add src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app.main import handler


class TestProfessorReady:
    """Complete test suite that works without any AWS dependencies"""
    
    def setup_method(self, method=None):
        """Set up test environment - NO AWS dependencies"""
        os.environ['DEV_MODE'] = 'true'
        os.environ['TABLE_NAME'] = 'test-table'
    
    def teardown_method(self, method=None):
        """Clean up environment variables"""
        for key in ['DEV_MODE', 'TABLE_NAME']:
            if key in os.environ:
                del os.environ[key]
    
    def _make_event(self, http_method, path, user_id='test-user', body=None, qs=None, headers=None):
        """Helper to create test events"""
        event_headers = {'X-MTP-Dev-User': user_id, 'Content-Type': 'application/json'}
        if headers:
            event_headers.update(headers)

        evt = {
            'httpMethod': http_method,
            'path': path,
            'headers': event_headers,
            'queryStringParameters': qs or {}
        }
        if body:
            evt['body'] = json.dumps(body)
        return evt
    
    # ==================== AUTHENTICATION TESTS ====================
    
    def test_dev_mode_authentication(self):
        """Test dev mode authentication with X-MTP-Dev-User header"""
        event = self._make_event('GET', '/v1/health', 'dev-user-123')
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['status'] == 'healthy'
    
    def test_health_endpoint_no_auth_required(self):
        """Test health endpoint bypasses authentication"""
        event = self._make_event('GET', '/v1/health', user_id=None, headers={})
        # Temporarily disable dev mode to test auth bypass
        original_dev_mode = os.environ.get('DEV_MODE')
        os.environ['DEV_MODE'] = 'false'
        
        try:
            result = handler(event, None)
            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['status'] == 'healthy'
        finally:
            if original_dev_mode:
                os.environ['DEV_MODE'] = original_dev_mode
    
    def test_unauthorized_request_production_mode(self):
        """Test unauthorized request in production mode"""
        original_dev_mode = os.environ.get('DEV_MODE')
        os.environ['DEV_MODE'] = 'false'
        
        try:
            event = self._make_event('GET', '/v1/notes', user_id=None, headers={})
            result = handler(event, None)
            assert result['statusCode'] == 401
            body = json.loads(result['body'])
            assert body['message'] == 'Unauthorized'
        finally:
            if original_dev_mode:
                os.environ['DEV_MODE'] = original_dev_mode
    
    # ==================== NOTES CRUD TESTS ====================
    
    @patch('app.repositories.dynamodb.db')
    def test_notes_create_success(self, mock_db):
        """Test successful note creation"""
        mock_db.create_note_item.return_value = {
            'PK': 'USER#test-user',
            'SK': 'NOTE#note-123',
            'text': 'Test note',
            'noteId': 'note-123'
        }
        mock_db.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        event = self._make_event('POST', '/v1/notes', 'test-user', {
            'text': 'Test note',
            'date': '2025-01-01T00:00:00Z',
            'direction': 'LONG'
        })
        
        result = handler(event, None)
        assert result['statusCode'] == 201
        body = json.loads(result['body'])
        assert body['message'] == 'Note created successfully'
        assert 'noteId' in body
        assert body['noteId'].startswith('note-')
        
        # Verify DynamoDB calls
        mock_db.create_note_item.assert_called_once()
        mock_db.put_item.assert_called_once()
    
    @patch('app.repositories.dynamodb.db')
    def test_notes_list_success(self, mock_db):
        """Test successful notes listing"""
        mock_db.query_gsi1.return_value = {
            'Items': [
                {
                    'noteId': 'note-1',
                    'text': 'First note',
                    'date': '2025-01-01T00:00:00Z',
                    'createdAt': '2025-01-01T00:00:00Z',
                    'updatedAt': '2025-01-01T00:00:00Z',
                    'direction': 'LONG'
                },
                {
                    'noteId': 'note-2',
                    'text': 'Second note',
                    'date': '2025-01-02T00:00:00Z',
                    'createdAt': '2025-01-02T00:00:00Z',
                    'updatedAt': '2025-01-02T00:00:00Z'
                }
            ]
        }
        
        event = self._make_event('GET', '/v1/notes', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        assert 'notes' in body
        assert len(body['notes']) == 2
        assert body['notes'][0]['noteId'] == 'note-1'
        assert body['notes'][0]['text'] == 'First note'
        assert body['notes'][0]['direction'] == 'LONG'
        assert body['notes'][1]['noteId'] == 'note-2'
        assert 'direction' not in body['notes'][1]  # Optional field filtering
        
        mock_db.query_gsi1.assert_called_once_with(
            gsi1pk='NOTE#test-user',
            limit=50,
            last_evaluated_key=None
        )
    
    @patch('app.repositories.dynamodb.db')
    def test_notes_list_with_pagination(self, mock_db):
        """Test notes listing with pagination"""
        mock_db.query_gsi1.return_value = {
            'Items': [{'noteId': 'note-1', 'text': 'Test note'}],
            'LastEvaluatedKey': {'PK': 'USER#test-user', 'SK': 'NOTE#note-1'}
        }
        
        event = self._make_event('GET', '/v1/notes', 'test-user', 
                               qs={'limit': '10', 'lastKey': '{"PK":"USER#test-user"}'})
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        assert 'notes' in body
        assert 'lastKey' in body
        assert len(body['notes']) == 1
        
        mock_db.query_gsi1.assert_called_once_with(
            gsi1pk='NOTE#test-user',
            limit=10,
            last_evaluated_key={'PK': 'USER#test-user'}
        )
    
    @patch('app.repositories.dynamodb.db')
    def test_notes_update_success(self, mock_db):
        """Test successful note update"""
        mock_db.get_item.return_value = {'noteId': 'note-123', 'text': 'Original text'}
        mock_db.update_item.return_value = {
            'Attributes': {
                'noteId': 'note-123',
                'text': 'Updated text',
                'direction': 'SHORT',
                'updatedAt': '2025-01-01T00:00:00Z'
            }
        }
        
        event = self._make_event('PATCH', '/v1/notes/note-123', 'test-user', {
            'text': 'Updated text',
            'direction': 'SHORT'
        })
        
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Note updated successfully'
        assert body['note']['text'] == 'Updated text'
        assert body['note']['direction'] == 'SHORT'
        
        mock_db.get_item.assert_called_once_with('USER#test-user', 'NOTE#note-123')
        mock_db.update_item.assert_called_once()
    
    @patch('app.repositories.dynamodb.db')
    def test_notes_update_not_found(self, mock_db):
        """Test note update when note doesn't exist"""
        mock_db.get_item.return_value = None
        
        event = self._make_event('PATCH', '/v1/notes/nonexistent', 'test-user', {
            'text': 'Updated text'
        })
        
        result = handler(event, None)
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['message'] == 'Note not found'
        
        mock_db.get_item.assert_called_once()
        mock_db.update_item.assert_not_called()
    
    @patch('app.repositories.dynamodb.db')
    def test_notes_delete_success(self, mock_db):
        """Test successful note deletion"""
        mock_db.get_item.return_value = {'noteId': 'note-123'}
        mock_db.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        event = self._make_event('DELETE', '/v1/notes/note-123', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Note deleted successfully'
        
        mock_db.get_item.assert_called_once_with('USER#test-user', 'NOTE#note-123')
        mock_db.delete_item.assert_called_once_with('USER#test-user', 'NOTE#note-123')
    
    @patch('app.repositories.dynamodb.db')
    def test_notes_delete_not_found(self, mock_db):
        """Test note deletion when note doesn't exist"""
        mock_db.get_item.return_value = None
        
        event = self._make_event('DELETE', '/v1/notes/nonexistent', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['message'] == 'Note not found'
        
        mock_db.get_item.assert_called_once()
        mock_db.delete_item.assert_not_called()
    
    # ==================== STRATEGIES CRUD TESTS ====================
    
    @patch('app.repositories.dynamodb.db')
    def test_strategies_create_success(self, mock_db):
        """Test successful strategy creation"""
        mock_db.create_strategy_item.return_value = {
            'PK': 'USER#test-user',
            'SK': 'STRAT#strat-123',
            'name': 'Test Strategy',
            'strategyId': 'strat-123'
        }
        mock_db.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        event = self._make_event('POST', '/v1/strategies', 'test-user', {
            'name': 'Test Strategy',
            'market': 'ES',
            'timeframe': '5m',
            'dsl': {'rules': 'test rules'}
        })
        
        result = handler(event, None)
        assert result['statusCode'] == 201
        body = json.loads(result['body'])
        assert body['message'] == 'Strategy created successfully'
        assert 'strategyId' in body
        assert body['strategyId'].startswith('strategy-')
        
        mock_db.create_strategy_item.assert_called_once()
        mock_db.put_item.assert_called_once()
    
    @patch('app.repositories.dynamodb.db')
    def test_strategies_list_success(self, mock_db):
        """Test successful strategies listing"""
        mock_db.query_gsi1.return_value = {
            'Items': [
                {
                    'strategyId': 'strat-1',
                    'name': 'Strategy One',
                    'market': 'ES',
                    'timeframe': '5m',
                    'dsl': '{"rules": "test"}',
                    'createdAt': '2025-01-01T00:00:00Z',
                    'updatedAt': '2025-01-01T00:00:00Z'
                },
                {
                    'strategyId': 'strat-2',
                    'name': 'Strategy Two',
                    'market': 'NQ',
                    'timeframe': '1m',
                    'dsl': '{"rules": "test2"}',
                    'createdAt': '2025-01-02T00:00:00Z',
                    'updatedAt': '2025-01-02T00:00:00Z'
                }
            ]
        }
        
        event = self._make_event('GET', '/v1/strategies', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        assert 'strategies' in body
        assert len(body['strategies']) == 2
        assert body['strategies'][0]['name'] == 'Strategy One'
        assert body['strategies'][0]['dsl'] == {'rules': 'test'}  # JSON parsed
        assert body['strategies'][1]['name'] == 'Strategy Two'
        
        mock_db.query_gsi1.assert_called_once_with(
            gsi1pk='STRAT#test-user',
            limit=50,
            last_evaluated_key=None
        )
    
    @patch('app.repositories.dynamodb.db')
    def test_strategies_get_single_success(self, mock_db):
        """Test successful single strategy retrieval"""
        mock_db.get_item.return_value = {
            'strategyId': 'strat-123',
            'name': 'Test Strategy',
            'market': 'ES',
            'timeframe': '5m',
            'dsl': '{"rules": "test rules"}',
            'createdAt': '2025-01-01T00:00:00Z',
            'updatedAt': '2025-01-01T00:00:00Z'
        }
        
        event = self._make_event('GET', '/v1/strategies/strat-123', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        strategy = body['strategy']
        assert strategy['strategyId'] == 'strat-123'
        assert strategy['name'] == 'Test Strategy'
        assert strategy['dsl'] == {'rules': 'test rules'}  # JSON parsed
        
        mock_db.get_item.assert_called_once_with('USER#test-user', 'STRAT#strat-123')
    
    @patch('app.repositories.dynamodb.db')
    def test_strategies_get_not_found(self, mock_db):
        """Test strategy retrieval when strategy doesn't exist"""
        mock_db.get_item.return_value = None
        
        event = self._make_event('GET', '/v1/strategies/nonexistent', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['message'] == 'Strategy not found'
        
        mock_db.get_item.assert_called_once()
    
    @patch('app.repositories.dynamodb.db')
    def test_strategies_update_success(self, mock_db):
        """Test successful strategy update"""
        mock_db.get_item.return_value = {'strategyId': 'strat-123', 'name': 'Original'}
        mock_db.update_item.return_value = {
            'Attributes': {
                'strategyId': 'strat-123',
                'name': 'Updated Strategy',
                'updatedAt': '2025-01-01T00:00:00Z'
            }
        }
        
        event = self._make_event('PATCH', '/v1/strategies/strat-123', 'test-user', {
            'name': 'Updated Strategy',
            'dsl': {'new': 'rules'}
        })
        
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Strategy updated successfully'
        
        mock_db.get_item.assert_called_once()
        mock_db.update_item.assert_called_once()
    
    @patch('app.repositories.dynamodb.db')
    def test_strategies_delete_success(self, mock_db):
        """Test successful strategy deletion"""
        mock_db.get_item.return_value = {'strategyId': 'strat-123'}
        mock_db.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        event = self._make_event('DELETE', '/v1/strategies/strat-123', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Strategy deleted successfully'
        
        mock_db.get_item.assert_called_once_with('USER#test-user', 'STRAT#strat-123')
        mock_db.delete_item.assert_called_once_with('USER#test-user', 'STRAT#strat-123')
    
    # ==================== REPORTING TESTS ====================
    
    @patch('app.repositories.dynamodb.db')
    def test_reports_notes_summary_success(self, mock_db):
        """Test successful notes summary reporting"""
        mock_db.query_gsi1.return_value = {
            'Items': [
                {'hit_miss': 'HIT', 'session': 'MORNING', 'win_amount': 100, 'date': '2025-01-01'},
                {'hit_miss': 'MISS', 'session': 'AFTERNOON', 'win_amount': 0, 'date': '2025-01-02'},
                {'hit_miss': 'HIT', 'session': 'MORNING', 'win_amount': 200, 'date': '2025-01-03'},
                {'hit_miss': 'UNKNOWN', 'session': 'EVENING', 'date': '2025-01-04'},  # No win_amount
            ]
        }
        
        event = self._make_event('GET', '/v1/reports/notes-summary', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        summary = body['summary']
        assert summary['totalNotes'] == 4
        assert summary['byHitMiss'] == {'HIT': 2, 'MISS': 1, 'UNKNOWN': 1}
        assert summary['bySession'] == {'MORNING': 2, 'AFTERNOON': 1, 'EVENING': 1}
        assert summary['averageWinAmount'] == 100.0  # (100+0+200)/3
        
        mock_db.query_gsi1.assert_called_once_with(
            'NOTE#test-user',
            limit=200
        )
    
    @patch('app.repositories.dynamodb.db')
    def test_reports_with_date_filter(self, mock_db):
        """Test notes summary with date filtering"""
        mock_db.query_gsi1.return_value = {
            'Items': [
                {'hit_miss': 'HIT', 'date': '2024-01-01'},  # Outside range
                {'hit_miss': 'MISS', 'date': '2025-01-01'},  # Inside range
                {'hit_miss': 'HIT', 'date': '2025-01-02'},   # Inside range
            ]
        }
        
        event = self._make_event('GET', '/v1/reports/notes-summary', 'test-user',
                               qs={'from': '2025-01-01', 'to': '2025-01-02'})
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        summary = body['summary']
        assert summary['totalNotes'] == 2  # Only 2 notes in date range
        assert summary['byHitMiss'] == {'HIT': 1, 'MISS': 1}
    
    # ==================== ERROR HANDLING TESTS ====================
    
    def test_not_found_endpoint(self):
        """Test 404 handling for unknown endpoints"""
        event = self._make_event('GET', '/v1/unknown-endpoint', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['message'] == 'Not found'
    
    @patch('app.core.auth.get_user_id_from_event')
    def test_internal_error_handling(self, mock_get_user_id):
        """Test internal error handling"""
        mock_get_user_id.side_effect = Exception("Simulated internal error")
        
        event = self._make_event('GET', '/v1/notes', 'test-user')
        result = handler(event, None)
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'Internal server error' in body['message']
    
    # ==================== CORS TESTS ====================
    
    def test_cors_headers_included(self):
        """Test that CORS headers are included in responses"""
        event = self._make_event('GET', '/v1/health', headers={'origin': 'https://example.com'})
        result = handler(event, None)
        assert result['statusCode'] == 200
        
        headers = result['headers']
        assert 'Access-Control-Allow-Origin' in headers
        assert 'Access-Control-Allow-Methods' in headers
        assert 'Access-Control-Allow-Headers' in headers
        assert headers['Access-Control-Allow-Origin'] == 'https://example.com'
    
    def test_cors_default_origin(self):
        """Test CORS headers with default origin"""
        event = self._make_event('GET', '/v1/health')
        result = handler(event, None)
        assert result['statusCode'] == 200
        
        headers = result['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
    
    # ==================== ADDITIONAL COVERAGE TESTS ====================
    
    def test_decimal_default_helper(self):
        """Test decimal_default helper function"""
        from decimal import Decimal
        from app.core.response import decimal_default
        
        # Test decimal conversion
        assert decimal_default(Decimal('10.5')) == 10.5
        
        # Test TypeError for non-decimal
        with pytest.raises(TypeError):
            decimal_default("not a decimal")
    
    @patch('app.repositories.dynamodb.db')
    def test_strategies_update_with_dsl_object(self, mock_db):
        """Test strategy update with DSL as object (should be JSON serialized)"""
        mock_db.get_item.return_value = {'strategyId': 'strat-123', 'name': 'Original'}
        mock_db.update_item.return_value = {
            'Attributes': {
                'strategyId': 'strat-123',
                'name': 'Updated Strategy',
                'dsl': '{"rules": "test"}'
            }
        }
        
        event = self._make_event('PATCH', '/v1/strategies/strat-123', 'test-user', {
            'name': 'Updated Strategy',
            'dsl': {'rules': 'test'}  # Object should be JSON serialized
        })
        
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Strategy updated successfully'
        
        # Verify the update call was made
        mock_db.update_item.assert_called_once()
    
    @patch('app.repositories.dynamodb.db')
    def test_strategies_update_with_dsl_string(self, mock_db):
        """Test strategy update with DSL as string (should pass through)"""
        mock_db.get_item.return_value = {'strategyId': 'strat-123', 'name': 'Original'}
        mock_db.update_item.return_value = {
            'Attributes': {
                'strategyId': 'strat-123',
                'name': 'Updated Strategy',
                'dsl': '{"rules": "test"}'
            }
        }
        
        event = self._make_event('PATCH', '/v1/strategies/strat-123', 'test-user', {
            'name': 'Updated Strategy',
            'dsl': '{"rules": "test"}'  # String should pass through unchanged
        })
        
        result = handler(event, None)
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['message'] == 'Strategy updated successfully'
        
        # Verify the update call was made
        mock_db.update_item.assert_called_once()
