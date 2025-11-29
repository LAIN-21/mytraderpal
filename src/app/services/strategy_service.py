"""Strategy business logic service."""
import json
from typing import Dict, Any, List, Optional

from app.repositories.dynamodb import db
from app.models.strategy import Strategy
from app.core.utils import generate_id, now_iso


class StrategyService:
    """Service for strategy business logic."""
    
    def create_strategy(self, user_id: str, data: Dict[str, Any]) -> str:
        """Create a new strategy and return its ID."""
        strategy_id = generate_id("strategy")
        item = db.create_strategy_item(user_id, strategy_id, data)
        db.put_item(item)
        return strategy_id
    
    def get_strategy(self, user_id: str, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get a strategy by ID."""
        pk, sk = f'USER#{user_id}', f'STRAT#{strategy_id}'
        item = db.get_item(pk, sk)
        if not item:
            return None
        return self._item_to_strategy_dict(item)
    
    def list_strategies(
        self,
        user_id: str,
        limit: int = 50,
        last_key: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List strategies with pagination."""
        resp = db.query_gsi1(gsi1pk=f'STRAT#{user_id}', limit=limit, last_evaluated_key=last_key)
        
        items = [self._item_to_strategy_dict(it) for it in resp.get('Items', [])]
        
        result = {'strategies': items}
        if 'LastEvaluatedKey' in resp:
            result['lastKey'] = resp['LastEvaluatedKey']
        return result
    
    def update_strategy(self, user_id: str, strategy_id: str, data: Dict[str, Any]) -> bool:
        """Update a strategy."""
        pk, sk = f'USER#{user_id}', f'STRAT#{strategy_id}'
        
        if not db.get_item(pk, sk):
            return False
        
        update_expression = "SET #updatedAt = :updatedAt"
        eav = {':updatedAt': now_iso()}
        ean = {'#updatedAt': 'updatedAt'}
        
        for field in ["name", "market", "timeframe", "dsl"]:
            if field in data and data[field] not in (None, ""):
                ean[f'#{field}'] = field
                # Handle DSL serialization
                if field == 'dsl' and not isinstance(data['dsl'], str):
                    eav[f':{field}'] = json.dumps(data['dsl'])
                else:
                    eav[f':{field}'] = data[field]
                update_expression += f", #{field} = :{field}"
        
        db.update_item(pk, sk, update_expression, eav, ean)
        return True
    
    def delete_strategy(self, user_id: str, strategy_id: str) -> bool:
        """Delete a strategy."""
        pk, sk = f'USER#{user_id}', f'STRAT#{strategy_id}'
        if not db.get_item(pk, sk):
            return False
        db.delete_item(pk, sk)
        return True
    
    def _item_to_strategy_dict(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB item to strategy dictionary."""
        dsl = self._parse_dsl(item.get('dsl'))
        return {
            'strategyId': item.get('strategyId'),
            'name': item.get('name'),
            'market': item.get('market'),
            'timeframe': item.get('timeframe'),
            'dsl': dsl,
            'createdAt': item.get('createdAt'),
            'updatedAt': item.get('updatedAt')
        }
    
    def _parse_dsl(self, dsl_value: Any) -> Dict[str, Any]:
        """Parse DSL value from DynamoDB item."""
        if not dsl_value:
            return {}
        if isinstance(dsl_value, dict):
            return dsl_value
        if isinstance(dsl_value, str):
            try:
                return json.loads(dsl_value)
            except json.JSONDecodeError:
                return {}
        return {}


# Service instance
strategy_service = StrategyService()

