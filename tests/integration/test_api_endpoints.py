"""Integration tests for API endpoints."""
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app.main import handler


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_endpoint_returns_200(self):
        """Test that health endpoint returns 200 status."""
        event = {
            'httpMethod': 'GET',
            'path': '/v1/health',
            'headers': {},
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] in ['healthy', 'degraded']
        assert 'timestamp' in body
        assert 'version' in body
        assert 'metrics' in body
    
    def test_health_endpoint_includes_metrics(self):
        """Test that health endpoint includes metrics."""
        event = {
            'httpMethod': 'GET',
            'path': '/v1/health',
            'headers': {},
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        body = json.loads(response['body'])
        
        metrics = body['metrics']
        assert 'requests_total' in metrics
        assert 'errors_total' in metrics
        assert 'error_rate' in metrics
        assert 'avg_latency_ms' in metrics
        assert 'uptime_seconds' in metrics


class TestMetricsEndpoint:
    """Test metrics endpoint."""
    
    def test_metrics_endpoint_returns_200(self):
        """Test that metrics endpoint returns 200 status."""
        event = {
            'httpMethod': 'GET',
            'path': '/v1/metrics',
            'headers': {},
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 200
        assert 'text/plain' in response['headers']['Content-Type']
        assert 'requests_total' in response['body']
        assert 'errors_total' in response['body']
    
    def test_metrics_endpoint_prometheus_format(self):
        """Test that metrics are in Prometheus format."""
        event = {
            'httpMethod': 'GET',
            'path': '/v1/metrics',
            'headers': {},
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        body = response['body']
        
        # Check Prometheus format
        assert '# HELP' in body
        assert '# TYPE' in body
        assert 'requests_total' in body
        assert 'errors_total' in body


class TestAuthentication:
    """Test authentication requirements."""
    
    def test_protected_endpoint_requires_auth(self):
        """Test that protected endpoints return 401 without auth."""
        event = {
            'httpMethod': 'GET',
            'path': '/v1/notes',
            'headers': {},
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'Unauthorized' in body.get('message', '')
    
    def test_health_endpoint_no_auth_required(self):
        """Test that health endpoint doesn't require auth."""
        event = {
            'httpMethod': 'GET',
            'path': '/v1/health',
            'headers': {},
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        assert response['statusCode'] == 200
    
    def test_metrics_endpoint_no_auth_required(self):
        """Test that metrics endpoint doesn't require auth."""
        event = {
            'httpMethod': 'GET',
            'path': '/v1/metrics',
            'headers': {},
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        assert response['statusCode'] == 200


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_for_unknown_endpoint(self):
        """Test that unknown endpoints return 404."""
        event = {
            'httpMethod': 'GET',
            'path': '/v1/unknown',
            'headers': {},
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'Not found' in body.get('message', '')
    
    def test_405_for_wrong_method(self):
        """Test that wrong HTTP method returns 405."""
        event = {
            'httpMethod': 'DELETE',
            'path': '/v1/health',
            'headers': {},
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert 'Method not allowed' in body.get('message', '')


class TestCORS:
    """Test CORS headers."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        event = {
            'httpMethod': 'GET',
            'path': '/v1/health',
            'headers': {
                'origin': 'https://example.com'
            },
            'queryStringParameters': None
        }
        
        response = handler(event, None)
        
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == 'https://example.com'

