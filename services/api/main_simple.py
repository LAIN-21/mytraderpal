import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

def decimal_default(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    """
    Simple Lambda handler for testing
    """
    try:
        # Get the HTTP method and path
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        path = event.get('path', event.get('rawPath', '/'))
        
        print(f"Received request: {http_method} {path}")
        print(f"Event: {json.dumps(event, indent=2)}")
        
        # Handle different endpoints
        if path == '/v1/health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                },
                'body': json.dumps({'message': 'API is healthy'})
            }
        
        elif path == '/v1/notes' and http_method == 'POST':
            # Create a new note
            body = json.loads(event.get('body', '{}'))
            
            # Get user ID from JWT token (simplified for now)
            user_id = 'test-user-123'  # This should come from JWT token
            
            note_id = f"note-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create note item
            note_item = {
                'PK': f'USER#{user_id}',
                'SK': f'NOTE#{note_id}',
                'entityType': 'NOTE',
                'noteId': note_id,
                'date': body.get('date', datetime.now().isoformat()),
                'text': body.get('text', ''),
                'direction': body.get('direction', ''),
                'session': body.get('session', ''),
                'risk': body.get('risk', 0),
                'win_amount': body.get('win_amount', 0),
                'strategyId': body.get('strategyId', ''),
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'GSI1PK': f'NOTE#{user_id}',
                'GSI1SK': f"{body.get('date', datetime.now().isoformat())}#{note_id}"
            }
            
            # Save to DynamoDB
            table.put_item(Item=note_item)
            
            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                },
                'body': json.dumps({
                    'message': 'Note created successfully',
                    'noteId': note_id
                })
            }
        
        elif path == '/v1/notes' and http_method == 'GET':
            # List notes
            user_id = 'test-user-123'  # This should come from JWT token
            
            # Query notes using GSI1
            response = table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :gsi1pk',
                ExpressionAttributeValues={
                    ':gsi1pk': f'NOTE#{user_id}'
                },
                ScanIndexForward=False  # Sort by date descending
            )
            
            notes = []
            for item in response.get('Items', []):
                notes.append({
                    'noteId': item.get('noteId'),
                    'date': item.get('date'),
                    'text': item.get('text'),
                    'direction': item.get('direction'),
                    'session': item.get('session'),
                    'risk': item.get('risk'),
                    'win_amount': item.get('win_amount'),
                    'strategyId': item.get('strategyId'),
                    'createdAt': item.get('createdAt'),
                    'updatedAt': item.get('updatedAt')
                })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                },
                'body': json.dumps({
                    'notes': notes
                }, default=decimal_default)
            }
        
        elif path == '/v1/strategies' and http_method == 'POST':
            # Create a new strategy
            body = json.loads(event.get('body', '{}'))
            
            # Get user ID from JWT token (simplified for now)
            user_id = 'test-user-123'  # This should come from JWT token
            
            strategy_id = f"strategy-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create strategy item
            strategy_item = {
                'PK': f'USER#{user_id}',
                'SK': f'STRAT#{strategy_id}',
                'entityType': 'STRATEGY',
                'strategyId': strategy_id,
                'name': body.get('name', ''),
                'market': body.get('market', ''),
                'timeframe': body.get('timeframe', ''),
                'dsl': json.dumps(body.get('dsl', {})),  # Store as JSON string
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'GSI1PK': f'STRAT#{user_id}',
                'GSI1SK': f"{datetime.now().isoformat()}#{strategy_id}"
            }
            
            # Save to DynamoDB
            table.put_item(Item=strategy_item)
            
            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                },
                'body': json.dumps({
                    'message': 'Strategy created successfully',
                    'strategyId': strategy_id
                })
            }
        
        elif path == '/v1/strategies' and http_method == 'GET':
            # List strategies
            user_id = 'test-user-123'  # This should come from JWT token
            
            # Query strategies using GSI1
            response = table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :gsi1pk',
                ExpressionAttributeValues={
                    ':gsi1pk': f'STRAT#{user_id}'
                },
                ScanIndexForward=False  # Sort by date descending
            )
            
            strategies = []
            for item in response.get('Items', []):
                # Parse DSL from JSON string back to object
                dsl = {}
                try:
                    dsl = json.loads(item.get('dsl', '{}'))
                except:
                    dsl = {}
                
                strategies.append({
                    'strategyId': item.get('strategyId'),
                    'name': item.get('name'),
                    'market': item.get('market'),
                    'timeframe': item.get('timeframe'),
                    'dsl': dsl,
                    'createdAt': item.get('createdAt'),
                    'updatedAt': item.get('updatedAt')
                })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                },
                'body': json.dumps({
                    'strategies': strategies
                }, default=decimal_default)
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                },
                'body': json.dumps({'message': 'Not found'})
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
            },
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }
