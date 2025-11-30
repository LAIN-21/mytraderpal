"""Note business logic service."""
import json
from typing import Dict, Any, List, Optional

from app.repositories.dynamodb import db
from app.models.note import Note
from app.core.utils import generate_id, now_iso


class NoteService:
    """Service for note business logic."""
    
    def create_note(self, user_id: str, data: Dict[str, Any]) -> str:
        """Create a new note and return its ID."""
        note_id = generate_id("note")
        item = db.create_note_item(user_id, note_id, data)
        db.put_item(item)
        return note_id
    
    def get_note(self, user_id: str, note_id: str) -> Optional[Dict[str, Any]]:
        """Get a note by ID."""
        pk, sk = f'USER#{user_id}', f'NOTE#{note_id}'
        item = db.get_item(pk, sk)
        if not item:
            return None
        return self._item_to_note_dict(item)
    
    def list_notes(
        self,
        user_id: str,
        limit: int = 50,
        last_key: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List notes with pagination."""
        resp = db.query_gsi1(gsi1pk=f'NOTE#{user_id}', limit=limit, last_evaluated_key=last_key)
        
        items = [self._item_to_note_dict(it) for it in resp.get('Items', [])]
        
        result = {'notes': items}
        if 'LastEvaluatedKey' in resp:
            result['lastKey'] = resp['LastEvaluatedKey']
        return result
    
    def update_note(self, user_id: str, note_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a note."""
        pk, sk = f'USER#{user_id}', f'NOTE#{note_id}'
        
        if not db.get_item(pk, sk):
            return None
        
        update_expression = "SET #updatedAt = :updatedAt"
        eav = {':updatedAt': now_iso()}
        ean = {'#updatedAt': 'updatedAt'}
        
        for field in ["date", "text", "direction", "session", "risk", "win_amount", "strategyId", "hit_miss"]:
            if field in data and data[field] not in (None, ""):
                ean[f'#{field}'] = field
                eav[f':{field}'] = data[field]
                update_expression += f", #{field} = :{field}"
        
        # If date changed, update GSI1SK
        if 'date' in data and data['date']:
            ean['#GSI1SK'] = 'GSI1SK'
            eav[':gsi1sk'] = f"{data['date']}#{note_id}"
            update_expression += ", #GSI1SK = :gsi1sk"
        
        updated = db.update_item(pk, sk, update_expression, eav, ean)['Attributes']
        return self._item_to_note_dict(updated)
    
    def delete_note(self, user_id: str, note_id: str) -> bool:
        """Delete a note."""
        pk, sk = f'USER#{user_id}', f'NOTE#{note_id}'
        if not db.get_item(pk, sk):
            return False
        db.delete_item(pk, sk)
        return True
    
    def _item_to_note_dict(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB item to note dictionary."""
        note = {
            'noteId': item.get('noteId'),
            'date': item.get('date'),
            'text': item.get('text', ''),
            'createdAt': item.get('createdAt'),
            'updatedAt': item.get('updatedAt'),
        }
        for field in ["direction", "session", "risk", "win_amount", "strategyId", "hit_miss"]:
            if field in item:
                note[field] = item[field]
        return note


# Service instance
note_service = NoteService()


