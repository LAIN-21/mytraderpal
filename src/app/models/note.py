"""Note domain model."""
from typing import Optional, Dict, Any
from datetime import datetime


class Note:
    """Note domain model."""
    
    ALLOWED_FIELDS = {
        "date", "text", "direction", "session", "risk", 
        "win_amount", "strategyId", "hit_miss"
    }
    
    def __init__(
        self,
        note_id: str,
        user_id: str,
        date: Optional[str] = None,
        text: Optional[str] = None,
        direction: Optional[str] = None,
        session: Optional[str] = None,
        risk: Optional[float] = None,
        win_amount: Optional[float] = None,
        strategy_id: Optional[str] = None,
        hit_miss: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.note_id = note_id
        self.user_id = user_id
        self.date = date
        self.text = text
        self.direction = direction
        self.session = session
        self.risk = risk
        self.win_amount = win_amount
        self.strategy_id = strategy_id
        self.hit_miss = hit_miss
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary."""
        result = {
            'noteId': self.note_id,
            'date': self.date,
            'text': self.text or '',
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
        # Add optional fields
        for field in ["direction", "session", "risk", "win_amount", "strategyId", "hit_miss"]:
            value = getattr(self, field.replace('Id', '_id').replace('_', ''), None)
            if value is not None:
                result[field] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Note':
        """Create note from dictionary."""
        return cls(
            note_id=data.get('noteId', ''),
            user_id=data.get('userId', ''),
            date=data.get('date'),
            text=data.get('text'),
            direction=data.get('direction'),
            session=data.get('session'),
            risk=data.get('risk'),
            win_amount=data.get('win_amount'),
            strategy_id=data.get('strategyId'),
            hit_miss=data.get('hit_miss'),
            created_at=data.get('createdAt'),
            updated_at=data.get('updatedAt')
        )

