"""Reports API controllers."""
from typing import Dict, Any

from app.services.report_service import report_service
from app.core.response import success_response, error_response, get_origin


def get_notes_summary(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Get summary report of notes with filtering."""
    try:
        qs = event.get('queryStringParameters') or {}
        date_from = qs.get('from') or ""
        date_to = qs.get('to') or ""
        limit = int(qs.get('limit', '200'))
        
        result = report_service.get_notes_summary(user_id, date_from, date_to, limit)
        return success_response(result, get_origin(event))
    except Exception as e:
        return error_response(500, f'Failed to generate report: {str(e)}', get_origin(event))

