"""Route dispatcher for API Gateway events."""
import time
import json
from typing import Dict, Any, Optional, Tuple

from app.core.auth import get_user_id_from_event
from app.core.response import error_response, get_origin, cors_headers
from app.core.metrics import get_metrics
from app.core.health import get_health_status
from app.api import notes, strategies, reports, metrics


def extract_path_params(path: str) -> Tuple[str, Optional[str]]:
    """
    Extract resource ID from path.
    Returns (base_path, resource_id)
    """
    parts = path.strip('/').split('/')
    if len(parts) >= 3:  # /v1/notes/{id} or /v1/strategies/{id}
        return f"/{parts[0]}/{parts[1]}", parts[2]
    return path, None


def route_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route the request to appropriate handler.
    Returns response dict.
    """
    start_time = time.time()
    metrics_collector = get_metrics()
    is_error = False
    
    try:
        # Extract request details
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('path') or event.get('rawPath', '/')
        origin = get_origin(event)
        
        # Handle CORS preflight requests
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers(origin),
                'body': ''
            }
        
        # Define valid paths and their allowed methods
        valid_paths = {
            '/v1/health': ['GET'],
            '/v1/metrics': ['GET'],
            '/v1/notes': ['GET', 'POST'],
            '/v1/strategies': ['GET', 'POST'],
            '/v1/reports/notes-summary': ['GET']
        }
        
        # Check if path is valid (exact match or starts with valid prefix)
        is_valid_path = (
            path in valid_paths or
            path.startswith('/v1/notes/') or
            path.startswith('/v1/strategies/')
        )
        
        # Return 404 for invalid paths before authentication
        if not is_valid_path:
            return error_response(404, 'Not found', origin)
        
        # Check HTTP method for valid paths
        if path in valid_paths:
            allowed_methods = valid_paths[path]
        elif path.startswith('/v1/notes/'):
            allowed_methods = ['GET', 'PUT', 'PATCH', 'DELETE']
        elif path.startswith('/v1/strategies/'):
            allowed_methods = ['GET', 'PUT', 'PATCH', 'DELETE']
        else:
            allowed_methods = []
        
        if http_method not in allowed_methods:
            return error_response(405, 'Method not allowed', origin)
        
        # Authentication (except for health and metrics endpoints)
        user_id = None
        if path not in ['/v1/health', '/v1/metrics']:
            try:
                user_id = get_user_id_from_event(event)
            except PermissionError:
                return error_response(401, 'Unauthorized', origin)
        
        # Route to appropriate handler
        if path == '/v1/health' and http_method == 'GET':
            health_data = get_health_status()
            response = {
                'statusCode': 200,
                'headers': cors_headers(origin),
                'body': json.dumps(health_data)
            }
            return response
        
        # Notes routes
        if path == '/v1/notes' and http_method == 'POST':
            response = notes.create_note(event, user_id)
        elif path == '/v1/notes' and http_method == 'GET':
            response = notes.list_notes(event, user_id)
        elif path.startswith('/v1/notes/') and http_method in ('GET', 'PUT', 'PATCH', 'DELETE'):
            base_path, note_id = extract_path_params(path)
            if not note_id:
                response = error_response(400, 'Note ID required', origin)
            elif http_method == 'GET':
                response = notes.get_note(event, user_id, note_id)
            elif http_method in ('PUT', 'PATCH'):
                response = notes.update_note(event, user_id, note_id)
            elif http_method == 'DELETE':
                response = notes.delete_note(event, user_id, note_id)
            else:
                response = error_response(405, 'Method not allowed', origin)
        
        # Strategies routes
        elif path == '/v1/strategies' and http_method == 'POST':
            response = strategies.create_strategy(event, user_id)
        elif path == '/v1/strategies' and http_method == 'GET':
            response = strategies.list_strategies(event, user_id)
        elif path.startswith('/v1/strategies/') and http_method in ('GET', 'PUT', 'PATCH', 'DELETE'):
            base_path, strategy_id = extract_path_params(path)
            if not strategy_id:
                response = error_response(400, 'Strategy ID required', origin)
            elif http_method == 'GET':
                response = strategies.get_strategy(event, user_id, strategy_id)
            elif http_method in ('PUT', 'PATCH'):
                response = strategies.update_strategy(event, user_id, strategy_id)
            elif http_method == 'DELETE':
                response = strategies.delete_strategy(event, user_id, strategy_id)
            else:
                response = error_response(405, 'Method not allowed', origin)
        
        # Reports routes
        elif path == '/v1/reports/notes-summary' and http_method == 'GET':
            response = reports.get_notes_summary(event, user_id)
        
        # Metrics route (no auth required for monitoring)
        elif path == '/v1/metrics' and http_method == 'GET':
            response = metrics.get_metrics_endpoint(event)
        
        # Not found
        else:
            response = error_response(404, 'Not found', origin)
            is_error = True
        
        # Record metrics
        latency_ms = (time.time() - start_time) * 1000
        status_code = response.get('statusCode', 500)
        is_error = is_error or (status_code >= 400)
        metrics_collector.record_request(latency_ms, is_error)
        
        return response
        
    except Exception as e:
        # Record error metric
        latency_ms = (time.time() - start_time) * 1000
        metrics_collector.record_request(latency_ms, is_error=True)
        
        # Return error response
        return error_response(
            500,
            f'Internal server error: {str(e)}',
            get_origin(event)
        )

