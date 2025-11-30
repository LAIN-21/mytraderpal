"""Strategies API controllers."""
import json
from typing import Dict, Any

from app.services.strategy_service import strategy_service
from app.core.response import success_response, error_response, get_origin


def create_strategy(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Create a new strategy."""
    try:
        body = json.loads(event.get('body') or '{}')
        strategy_id = strategy_service.create_strategy(user_id, body)
        return success_response(
            {'message': 'Strategy created successfully', 'strategyId': strategy_id},
            get_origin(event),
            201
        )
    except Exception as e:
        return error_response(400, f'Failed to create strategy: {str(e)}', get_origin(event))


def list_strategies(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """List strategies with pagination."""
    try:
        qs = event.get('queryStringParameters') or {}
        limit = int(qs.get('limit', '50'))
        lek = qs.get('lastKey')
        last_key = json.loads(lek) if lek else None
        
        result = strategy_service.list_strategies(user_id, limit, last_key)
        return success_response(result, get_origin(event))
    except Exception as e:
        return error_response(500, f'Failed to list strategies: {str(e)}', get_origin(event))


def get_strategy(event: Dict[str, Any], user_id: str, strategy_id: str) -> Dict[str, Any]:
    """Get a single strategy by ID."""
    try:
        strategy = strategy_service.get_strategy(user_id, strategy_id)
        if not strategy:
            return error_response(404, 'Strategy not found', get_origin(event))
        return success_response({'strategy': strategy}, get_origin(event))
    except Exception as e:
        return error_response(500, f'Failed to get strategy: {str(e)}', get_origin(event))


def update_strategy(event: Dict[str, Any], user_id: str, strategy_id: str) -> Dict[str, Any]:
    """Update an existing strategy."""
    try:
        body = json.loads(event.get('body') or '{}')
        if not strategy_service.update_strategy(user_id, strategy_id, body):
            return error_response(404, 'Strategy not found', get_origin(event))
        return success_response(
            {'message': 'Strategy updated successfully'},
            get_origin(event)
        )
    except Exception as e:
        return error_response(500, f'Failed to update strategy: {str(e)}', get_origin(event))


def delete_strategy(event: Dict[str, Any], user_id: str, strategy_id: str) -> Dict[str, Any]:
    """Delete a strategy."""
    try:
        if not strategy_service.delete_strategy(user_id, strategy_id):
            return error_response(404, 'Strategy not found', get_origin(event))
        return success_response({'message': 'Strategy deleted successfully'}, get_origin(event))
    except Exception as e:
        return error_response(500, f'Failed to delete strategy: {str(e)}', get_origin(event))


