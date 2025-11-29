"""Report generation service."""
from typing import Dict, Any, List

from app.repositories.dynamodb import db


class ReportService:
    """Service for generating reports."""
    
    def get_notes_summary(
        self,
        user_id: str,
        date_from: str = "",
        date_to: str = "",
        limit: int = 200
    ) -> Dict[str, Any]:
        """Generate summary report of notes."""
        # Query all notes for user
        resp = db.query_gsi1(f'NOTE#{user_id}', limit=limit)
        notes = resp.get('Items', [])
        
        # Filter by date range if provided
        filtered = [n for n in notes if self._in_date_range(n.get('date', ''), date_from, date_to)]
        
        # Calculate statistics
        total = len(filtered)
        by_hit = {}
        by_session = {}
        win_sum, win_count = 0.0, 0
        
        for note in filtered:
            # Hit/Miss distribution
            hm = note.get('hit_miss', 'UNKNOWN')
            by_hit[hm] = by_hit.get(hm, 0) + 1
            
            # Session distribution
            sess = note.get('session', 'UNKNOWN')
            by_session[sess] = by_session.get(sess, 0) + 1
            
            # Win amount calculation
            if 'win_amount' in note:
                try:
                    win_sum += float(note['win_amount'])
                    win_count += 1
                except (ValueError, TypeError):
                    pass
        
        avg_win = (win_sum / win_count) if win_count > 0 else 0.0
        
        return {
            'summary': {
                'totalNotes': total,
                'byHitMiss': by_hit,
                'bySession': by_session,
                'averageWinAmount': round(avg_win, 2)
            }
        }
    
    def _in_date_range(self, date_str: str, date_from: str, date_to: str) -> bool:
        """Check if date is in range."""
        if not date_str:
            return True
        if date_from and date_str < date_from:
            return False
        if date_to and date_str > date_to:
            return False
        return True


# Service instance
report_service = ReportService()

