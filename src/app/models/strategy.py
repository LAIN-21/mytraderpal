"""Strategy domain model."""
from typing import Optional, Dict, Any


class Strategy:
    """Strategy domain model."""
    
    ALLOWED_FIELDS = {"name", "market", "timeframe", "dsl"}
    
    def __init__(
        self,
        strategy_id: str,
        user_id: str,
        name: str,
        market: str,
        timeframe: str,
        dsl: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.strategy_id = strategy_id
        self.user_id = user_id
        self.name = name
        self.market = market
        self.timeframe = timeframe
        self.dsl = dsl or {}
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert strategy to dictionary."""
        return {
            'strategyId': self.strategy_id,
            'name': self.name,
            'market': self.market,
            'timeframe': self.timeframe,
            'dsl': self.dsl,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Strategy':
        """Create strategy from dictionary."""
        return cls(
            strategy_id=data.get('strategyId', ''),
            user_id=data.get('userId', ''),
            name=data.get('name', ''),
            market=data.get('market', ''),
            timeframe=data.get('timeframe', ''),
            dsl=data.get('dsl', {}),
            created_at=data.get('createdAt'),
            updated_at=data.get('updatedAt')
        )

