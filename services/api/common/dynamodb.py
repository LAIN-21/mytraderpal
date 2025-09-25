import boto3
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class DynamoDBClient:
    def __init__(self):
        self.table_name = os.getenv('TABLE_NAME', 'mtp_app')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)
    
    def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Put an item into DynamoDB."""
        return self.table.put_item(Item=item)
    
    def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """Get an item from DynamoDB."""
        response = self.table.get_item(Key={'PK': pk, 'SK': sk})
        return response.get('Item')
    
    def delete_item(self, pk: str, sk: str) -> Dict[str, Any]:
        """Delete an item from DynamoDB."""
        return self.table.delete_item(Key={'PK': pk, 'SK': sk})
    
    def query_items(self, pk: str, sk_condition: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query items by partition key."""
        query_params = {
            'KeyConditionExpression': 'PK = :pk'
        }
        expression_values = {':pk': pk}
        
        if sk_condition:
            query_params['KeyConditionExpression'] += ' AND begins_with(SK, :sk)'
            expression_values[':sk'] = sk_condition
        
        query_params['ExpressionAttributeValues'] = expression_values
        
        response = self.table.query(**query_params)
        return response.get('Items', [])
    
    def query_gsi1(self, gsi1pk: str, limit: Optional[int] = None, 
                   last_evaluated_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query GSI1 for listing items."""
        query_params = {
            'IndexName': 'GSI1',
            'KeyConditionExpression': 'GSI1PK = :gsi1pk',
            'ExpressionAttributeValues': {':gsi1pk': gsi1pk},
            'ScanIndexForward': False,  # Sort by GSI1SK descending
        }
        
        if limit:
            query_params['Limit'] = limit
        
        if last_evaluated_key:
            query_params['ExclusiveStartKey'] = last_evaluated_key
        
        return self.table.query(**query_params)
    
    def update_item(self, pk: str, sk: str, update_expression: str, 
                   expression_values: Dict[str, Any]) -> Dict[str, Any]:
        """Update an item in DynamoDB."""
        return self.table.update_item(
            Key={'PK': pk, 'SK': sk},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )


def create_note_item(user_id: str, note_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a note item for DynamoDB."""
    now = datetime.utcnow().isoformat()
    
    item = {
        'PK': f'USER#{user_id}',
        'SK': f'NOTE#{note_id}',
        'GSI1PK': f'NOTE#{user_id}',
        'GSI1SK': f'{data.get("date", now)}#{note_id}',
        'entityType': 'NOTE',
        'noteId': note_id,
        'userId': user_id,
        'createdAt': now,
        'updatedAt': now,
        **data
    }
    
    return item


def create_strategy_item(user_id: str, strategy_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a strategy item for DynamoDB."""
    now = datetime.utcnow().isoformat()
    
    item = {
        'PK': f'USER#{user_id}',
        'SK': f'STRAT#{strategy_id}',
        'GSI1PK': f'STRAT#{user_id}',
        'GSI1SK': f'{now}#{strategy_id}',
        'entityType': 'STRATEGY',
        'strategyId': strategy_id,
        'userId': user_id,
        'createdAt': now,
        'updatedAt': now,
        **data
    }
    
    return item
