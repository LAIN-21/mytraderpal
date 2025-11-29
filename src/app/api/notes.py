"""Notes API controllers."""
import json
from typing import Dict, Any

from app.services.note_service import note_service
from app.core.response import success_response, error_response, get_origin


def create_note(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Create a new note."""
    try:
        body = json.loads(event.get('body') or '{}')
        note_id = note_service.create_note(user_id, body)
        return success_response(
            {'message': 'Note created successfully', 'noteId': note_id},
            get_origin(event),
            201
        )
    except Exception as e:
        return error_response(400, f'Failed to create note: {str(e)}', get_origin(event))


def list_notes(event: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """List notes with pagination."""
    try:
        qs = event.get('queryStringParameters') or {}
        limit = int(qs.get('limit', '50'))
        lek = qs.get('lastKey')
        last_key = json.loads(lek) if lek else None
        
        result = note_service.list_notes(user_id, limit, last_key)
        return success_response(result, get_origin(event))
    except Exception as e:
        return error_response(500, f'Failed to list notes: {str(e)}', get_origin(event))


def get_note(event: Dict[str, Any], user_id: str, note_id: str) -> Dict[str, Any]:
    """Get a single note by ID."""
    try:
        note = note_service.get_note(user_id, note_id)
        if not note:
            return error_response(404, 'Note not found', get_origin(event))
        return success_response({'note': note}, get_origin(event))
    except Exception as e:
        return error_response(500, f'Failed to get note: {str(e)}', get_origin(event))


def update_note(event: Dict[str, Any], user_id: str, note_id: str) -> Dict[str, Any]:
    """Update an existing note."""
    try:
        body = json.loads(event.get('body') or '{}')
        updated = note_service.update_note(user_id, note_id, body)
        if not updated:
            return error_response(404, 'Note not found', get_origin(event))
        return success_response(
            {'message': 'Note updated successfully', 'note': updated},
            get_origin(event)
        )
    except Exception as e:
        return error_response(500, f'Failed to update note: {str(e)}', get_origin(event))


def delete_note(event: Dict[str, Any], user_id: str, note_id: str) -> Dict[str, Any]:
    """Delete a note."""
    try:
        if not note_service.delete_note(user_id, note_id):
            return error_response(404, 'Note not found', get_origin(event))
        return success_response({'message': 'Note deleted successfully'}, get_origin(event))
    except Exception as e:
        return error_response(500, f'Failed to delete note: {str(e)}', get_origin(event))

