import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key


ALLOWED_NOTE_FIELDS = {
    "date", "text", "direction", "session", "risk", "win_amount", "strategyId", "hit_miss"
}
ALLOWED_STRATEGY_FIELDS = {"name", "market", "timeframe", "dsl"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DynamoDBClient:
    def __init__(self):
        self.table_name = os.getenv('TABLE_NAME', 'mtp_app')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)

    # ---------- primitives ----------
    def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Idempotent create (fails if the item already exists)."""
        return self.table.put_item(
            Item=item,
            ConditionExpression='attribute_not_exists(PK) AND attribute_not_exists(SK)'
        )

    def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        resp = self.table.get_item(Key={'PK': pk, 'SK': sk})
        return resp.get('Item')

    def delete_item(self, pk: str, sk: str) -> Dict[str, Any]:
        return self.table.delete_item(Key={'PK': pk, 'SK': sk})

    def update_item(self, pk: str, sk: str, update_expression: str,
                    expression_values: Dict[str, Any],
                    expression_attribute_names: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        params = {
            'Key': {'PK': pk, 'SK': sk},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_values,
            'ReturnValues': 'ALL_NEW'
        }
        if expression_attribute_names:
            params['ExpressionAttributeNames'] = expression_attribute_names
        return self.table.update_item(**params)

    # ---------- queries ----------
    def query_pk(self, pk: str, sk_begins_with: Optional[str] = None,
                 limit: int = 50,
                 last_evaluated_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        expr = Key('PK').eq(pk)
        if sk_begins_with:
            expr = expr & Key('SK').begins_with(sk_begins_with)

        params = {'KeyConditionExpression': expr, 'Limit': limit}
        if last_evaluated_key:
            params['ExclusiveStartKey'] = last_evaluated_key
        return self.table.query(**params)

    def query_gsi1(self, gsi1pk: str, limit: int = 50,
                   last_evaluated_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {
            'IndexName': 'GSI1',
            'KeyConditionExpression': Key('GSI1PK').eq(gsi1pk),
            'ScanIndexForward': False,
            'Limit': limit
        }
        if last_evaluated_key:
            params['ExclusiveStartKey'] = last_evaluated_key
        return self.table.query(**params)

    # ---------- builders ----------
    def create_note_item(self, user_id: str, note_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        now = _now_iso()
        payload = {k: v for k, v in (data or {}).items()
                   if k in ALLOWED_NOTE_FIELDS and v not in (None, "")}
        date_val = payload.get("date", now)
        return {
            'PK': f'USER#{user_id}',
            'SK': f'NOTE#{note_id}',
            'GSI1PK': f'NOTE#{user_id}',
            'GSI1SK': f'{date_val}#{note_id}',
            'entityType': 'NOTE',
            'noteId': note_id,
            'userId': user_id,
            'createdAt': now,
            'updatedAt': now,
            **payload
        }

    def create_strategy_item(self, user_id: str, strategy_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        now = _now_iso()
        payload = {k: v for k, v in (data or {}).items()
                   if k in ALLOWED_STRATEGY_FIELDS and v not in (None, "")}
        return {
            'PK': f'USER#{user_id}',
            'SK': f'STRAT#{strategy_id}',
            'GSI1PK': f'STRAT#{user_id}',
            'GSI1SK': f'{now}#{strategy_id}',
            'entityType': 'STRATEGY',
            'strategyId': strategy_id,
            'userId': user_id,
            'createdAt': now,
            'updatedAt': now,
            **payload
        }


# Reusable module-level client (warm Lambda reuse)
db = DynamoDBClient()