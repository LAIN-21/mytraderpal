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
            print(f"Creating note with body: {body}")
            print(f"hit_miss field: {body.get('hit_miss', 'NOT_FOUND')}")
            
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
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat(),
                'GSI1PK': f'NOTE#{user_id}',
                'GSI1SK': f"{body.get('date', datetime.now().isoformat())}#{note_id}"
            }
            
            # Only add optional fields if they have values
            optional_fields = ['direction', 'session', 'risk', 'win_amount', 'strategyId', 'hit_miss']
            for field in optional_fields:
                value = body.get(field)
                if value is not None and value != '':
                    note_item[field] = value
            print(f"Note item being created: {note_item}")
            print(f"hit_miss value in note_item: {note_item.get('hit_miss', 'NOT_FOUND')}")
            
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
                note = {
                    'noteId': item.get('noteId'),
                    'date': item.get('date'),
                    'text': item.get('text', ''),
                    'createdAt': item.get('createdAt'),
                    'updatedAt': item.get('updatedAt')
                }
                
                # Only include optional fields if they exist
                optional_fields = ['direction', 'session', 'risk', 'win_amount', 'strategyId', 'hit_miss']
                for field in optional_fields:
                    if field in item:
                        note[field] = item[field]
                
                notes.append(note)
            
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

        elif path.startswith('/v1/strategies/') and http_method == 'GET':
            # Get a specific strategy
            strategy_id = path.split('/')[-1]
            user_id = 'test-user-123'  # This should come from JWT token

            try:
                response = table.get_item(
                    Key={
                        'PK': f'USER#{user_id}',
                        'SK': f'STRAT#{strategy_id}'
                    }
                )

                if 'Item' not in response:
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                        },
                        'body': json.dumps({'message': 'Strategy not found'})
                    }

                item = response['Item']
                # Parse DSL JSON
                dsl = {}
                try:
                    dsl = json.loads(item.get('dsl', '{}'))
                except:
                    dsl = {}

                strategy = {
                    'strategyId': item.get('strategyId'),
                    'name': item.get('name'),
                    'market': item.get('market'),
                    'timeframe': item.get('timeframe'),
                    'dsl': dsl,
                    'createdAt': item.get('createdAt'),
                    'updatedAt': item.get('updatedAt'),
                }

                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({'strategy': strategy}, default=decimal_default)
                }

            except Exception as e:
                print(f"Error getting strategy: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({'message': f'Error getting strategy: {str(e)}'})
                }

        elif path.startswith('/v1/strategies/') and http_method == 'PUT':
            # Update a strategy
            strategy_id = path.split('/')[-1]
            body = json.loads(event.get('body', '{}'))
            user_id = 'test-user-123'  # This should come from JWT token

            try:
                # Ensure item exists
                response = table.get_item(Key={'PK': f'USER#{user_id}', 'SK': f'STRAT#{strategy_id}'})
                if 'Item' not in response:
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                        },
                        'body': json.dumps({'message': 'Strategy not found'})
                    }

                update_expression = 'SET #updatedAt = :updatedAt'
                expression_values = {':updatedAt': datetime.now().isoformat()}
                attribute_names = {'#updatedAt': 'updatedAt'}

                # Updatable fields
                if 'name' in body and body['name'] != '':
                    attribute_names['#name'] = 'name'
                    expression_values[':name'] = body['name']
                    update_expression += ', #name = :name'
                if 'market' in body and body['market'] != '':
                    attribute_names['#market'] = 'market'
                    expression_values[':market'] = body['market']
                    update_expression += ', #market = :market'
                if 'timeframe' in body and body['timeframe'] != '':
                    attribute_names['#timeframe'] = 'timeframe'
                    expression_values[':timeframe'] = body['timeframe']
                    update_expression += ', #timeframe = :timeframe'
                if 'dsl' in body and body['dsl'] is not None:
                    attribute_names['#dsl'] = 'dsl'
                    expression_values[':dsl'] = json.dumps(body['dsl'])
                    update_expression += ', #dsl = :dsl'

                table.update_item(
                    Key={'PK': f'USER#{user_id}', 'SK': f'STRAT#{strategy_id}'},
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_values,
                    ExpressionAttributeNames=attribute_names,
                )

                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({'message': 'Strategy updated successfully'})
                }

            except Exception as e:
                print(f"Error updating strategy: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({'message': f'Error updating strategy: {str(e)}'})
                }

        elif path.startswith('/v1/strategies/') and http_method == 'DELETE':
            # Delete a strategy
            strategy_id = path.split('/')[-1]
            user_id = 'test-user-123'  # This should come from JWT token

            try:
                # Check if strategy exists
                response = table.get_item(
                    Key={'PK': f'USER#{user_id}', 'SK': f'STRAT#{strategy_id}'}
                )

                if 'Item' not in response:
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                        },
                        'body': json.dumps({'message': 'Strategy not found'})
                    }

                table.delete_item(Key={'PK': f'USER#{user_id}', 'SK': f'STRAT#{strategy_id}'})

                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({'message': 'Strategy deleted successfully'})
                }

            except Exception as e:
                print(f"Error deleting strategy: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({'message': f'Error deleting strategy: {str(e)}'})
                }
        
        elif path.startswith('/v1/notes/') and http_method == 'PUT':
            # Update a note
            note_id = path.split('/')[-1]
            body = json.loads(event.get('body', '{}'))
            print(f"Updating note {note_id} with body: {body}")
            print(f"hit_miss field: {body.get('hit_miss', 'NOT_FOUND')}")
            
            user_id = 'test-user-123'  # This should come from JWT token
            
            # Check if note exists
            try:
                response = table.get_item(
                    Key={
                        'PK': f'USER#{user_id}',
                        'SK': f'NOTE#{note_id}'
                    }
                )
                
                if 'Item' not in response:
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                        },
                        'body': json.dumps({'message': 'Note not found'})
                    }
                
                # Build update expression using ExpressionAttributeNames to avoid reserved words
                update_expression = "SET #updatedAt = :updatedAt"
                expression_values = {
                    ':updatedAt': datetime.now().isoformat()
                }
                attribute_names = {
                    '#updatedAt': 'updatedAt'
                }

                # Add fields to update (map all attribute names to placeholders)
                fields_to_update = ['date', 'text', 'direction', 'session', 'risk', 'win_amount', 'strategyId', 'hit_miss']
                for field in fields_to_update:
                    if field in body and body[field] is not None and body[field] != '':
                        placeholder_name = f"#{field}"
                        attribute_names[placeholder_name] = field
                        update_expression += f", {placeholder_name} = :{field}"
                        expression_values[f':{field}'] = body[field]

                # Update GSI1SK if date changed
                if 'date' in body and body['date']:
                    attribute_names['#GSI1SK'] = 'GSI1SK'
                    update_expression += ", #GSI1SK = :gsi1sk"
                    expression_values[':gsi1sk'] = f"{body['date']}#{note_id}"
                
                # Update the item
                table.update_item(
                    Key={
                        'PK': f'USER#{user_id}',
                        'SK': f'NOTE#{note_id}'
                    },
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_values,
                    ExpressionAttributeNames=attribute_names
                )
                
                # Get the updated item
                updated_response = table.get_item(
                    Key={
                        'PK': f'USER#{user_id}',
                        'SK': f'NOTE#{note_id}'
                    }
                )
                
                updated_note = updated_response['Item']
                
                # Build response note with only existing fields
                response_note = {
                    'noteId': updated_note.get('noteId'),
                    'date': updated_note.get('date'),
                    'text': updated_note.get('text', ''),
                    'createdAt': updated_note.get('createdAt'),
                    'updatedAt': updated_note.get('updatedAt')
                }
                
                # Only include optional fields if they exist
                optional_fields = ['direction', 'session', 'risk', 'win_amount', 'strategyId', 'hit_miss']
                for field in optional_fields:
                    if field in updated_note:
                        response_note[field] = updated_note[field]
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({
                        'message': 'Note updated successfully',
                        'note': response_note
                    }, default=decimal_default)
                }
                
            except Exception as e:
                print(f"Error updating note: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({'message': f'Error updating note: {str(e)}'})
                }
        
        elif path.startswith('/v1/notes/') and http_method == 'DELETE':
            # Delete a note
            note_id = path.split('/')[-1]
            user_id = 'test-user-123'  # This should come from JWT token
            
            try:
                # Check if note exists
                response = table.get_item(
                    Key={
                        'PK': f'USER#{user_id}',
                        'SK': f'NOTE#{note_id}'
                    }
                )
                
                if 'Item' not in response:
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                        },
                        'body': json.dumps({'message': 'Note not found'})
                    }
                
                # Delete the item
                table.delete_item(
                    Key={
                        'PK': f'USER#{user_id}',
                        'SK': f'NOTE#{note_id}'
                    }
                )
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({'message': 'Note deleted successfully'})
                }
                
            except Exception as e:
                print(f"Error deleting note: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MTP-Dev-User'
                    },
                    'body': json.dumps({'message': f'Error deleting note: {str(e)}'})
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
