import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pytest
from moto import mock_aws
import boto3

# Add src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app.repositories.dynamodb import DynamoDBRepository, ALLOWED_NOTE_FIELDS, ALLOWED_STRATEGY_FIELDS


class TestDynamoDBRepository:
    @patch.dict(os.environ, {'TABLE_NAME': 'test-table', 'AWS_REGION': 'us-east-1'})
    def test_init(self):
        """Test DynamoDBRepository initialization"""
        client = DynamoDBRepository()
        assert client.table_name == 'test-table'
        assert client.table is not None
    
    @patch.dict(os.environ, {'AWS_REGION': 'us-east-1'})
    def test_init_default_table_name(self):
        """Test DynamoDBRepository initialization with default table name"""
        client = DynamoDBRepository()
        assert client.table_name == 'mtp_app'
    
    @mock_aws
    @patch.dict(os.environ, {'TABLE_NAME': 'test-table', 'AWS_REGION': 'us-east-1'})
    def test_put_item_with_condition(self):
        """Test put_item with condition expression"""
        # Create mock table
        ddb = boto3.client('dynamodb', region_name='us-east-1')
        ddb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        client = DynamoDBRepository()
        item = {
            'PK': 'USER#test',
            'SK': 'NOTE#test',
            'data': 'test'
        }
        
        result = client.put_item(item)
        assert result is not None
    
    @mock_aws
    @patch.dict(os.environ, {'TABLE_NAME': 'test-table', 'AWS_REGION': 'us-east-1'})
    def test_get_item(self):
        """Test get_item"""
        # Create mock table
        ddb = boto3.client('dynamodb', region_name='us-east-1')
        ddb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        client = DynamoDBRepository()
        
        # Test getting non-existent item
        result = client.get_item('USER#test', 'NOTE#test')
        assert result is None
    
    @mock_aws
    @patch.dict(os.environ, {'TABLE_NAME': 'test-table', 'AWS_REGION': 'us-east-1'})
    def test_delete_item(self):
        """Test delete_item"""
        # Create mock table
        ddb = boto3.client('dynamodb', region_name='us-east-1')
        ddb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        client = DynamoDBRepository()
        result = client.delete_item('USER#test', 'NOTE#test')
        assert result is not None
    
    @mock_aws
    @patch.dict(os.environ, {'TABLE_NAME': 'test-table', 'AWS_REGION': 'us-east-1'})
    def test_update_item(self):
        """Test update_item"""
        # Create mock table
        ddb = boto3.client('dynamodb', region_name='us-east-1')
        ddb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        client = DynamoDBRepository()
        
        # Test update with expression attribute names
        result = client.update_item(
            'USER#test', 
            'NOTE#test',
            'SET #attr = :val',
            {':val': 'test-value'},
            {'#attr': 'test_attribute'}
        )
        assert result is not None
    
    @mock_aws
    @patch.dict(os.environ, {'TABLE_NAME': 'test-table', 'AWS_REGION': 'us-east-1'})
    def test_query_pk(self):
        """Test query_pk method"""
        # Create mock table
        ddb = boto3.client('dynamodb', region_name='us-east-1')
        ddb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        client = DynamoDBRepository()
        result = client.query_pk('USER#test')
        assert result is not None
        assert 'Items' in result
    
    @mock_aws
    @patch.dict(os.environ, {'TABLE_NAME': 'test-table', 'AWS_REGION': 'us-east-1'})
    def test_query_pk_with_sk_begins_with(self):
        """Test query_pk with sk_begins_with parameter"""
        # Create mock table
        ddb = boto3.client('dynamodb', region_name='us-east-1')
        ddb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        client = DynamoDBRepository()
        result = client.query_pk('USER#test', sk_begins_with='NOTE#')
        assert result is not None
        assert 'Items' in result
    
    @mock_aws
    @patch.dict(os.environ, {'TABLE_NAME': 'test-table', 'AWS_REGION': 'us-east-1'})
    def test_query_gsi1(self):
        """Test query_gsi1 method"""
        # Create mock table with GSI
        ddb = boto3.client('dynamodb', region_name='us-east-1')
        ddb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1SK', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[{
                'IndexName': 'GSI1',
                'KeySchema': [
                    {'AttributeName': 'GSI1PK', 'KeyType': 'HASH'},
                    {'AttributeName': 'GSI1SK', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            }],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        
        client = DynamoDBRepository()
        result = client.query_gsi1('NOTE#test')
        assert result is not None
        assert 'Items' in result
    
    def test_create_note_item_basic(self):
        """Test create_note_item with basic data"""
        client = DynamoDBRepository()
        item = client.create_note_item('user-123', 'note-456', {
            'text': 'Test note',
            'date': '2025-01-01T00:00:00Z'
        })
        
        assert item['PK'] == 'USER#user-123'
        assert item['SK'] == 'NOTE#note-456'
        assert item['GSI1PK'] == 'NOTE#user-123'
        assert item['GSI1SK'].startswith('2025-01-01T00:00:00Z#')
        assert item['entityType'] == 'NOTE'
        assert item['noteId'] == 'note-456'
        assert item['userId'] == 'user-123'
        assert item['text'] == 'Test note'
        assert item['date'] == '2025-01-01T00:00:00Z'
        assert 'createdAt' in item
        assert 'updatedAt' in item
    
    def test_create_note_item_filters_allowed_fields(self):
        """Test create_note_item filters only allowed fields"""
        client = DynamoDBRepository()
        data = {
            'text': 'Test note',
            'date': '2025-01-01T00:00:00Z',
            'direction': 'LONG',
            'session': 'MORNING',
            'risk': 100,
            'win_amount': 150,
            'strategyId': 'strat-123',
            'hit_miss': 'HIT',
            'invalid_field': 'should_be_filtered',
            'another_invalid': 'also_filtered'
        }
        
        item = client.create_note_item('user-123', 'note-456', data)
        
        # Check allowed fields are present
        for field in ALLOWED_NOTE_FIELDS:
            if field in data:
                assert item[field] == data[field]
        
        # Check invalid fields are filtered out
        assert 'invalid_field' not in item
        assert 'another_invalid' not in item
    
    def test_create_note_item_filters_none_empty_values(self):
        """Test create_note_item filters None and empty values"""
        client = DynamoDBRepository()
        data = {
            'text': 'Test note',
            'date': '2025-01-01T00:00:00Z',
            'direction': None,
            'session': '',
            'risk': 100,
            'win_amount': 0  # 0 should be kept
        }
        
        item = client.create_note_item('user-123', 'note-456', data)
        
        assert item['text'] == 'Test note'
        assert item['date'] == '2025-01-01T00:00:00Z'
        assert item['risk'] == 100
        assert item['win_amount'] == 0
        assert 'direction' not in item
        assert 'session' not in item
    
    def test_create_note_item_defaults_date(self):
        """Test create_note_item defaults date when not provided"""
        client = DynamoDBRepository()
        item = client.create_note_item('user-123', 'note-456', {'text': 'Test note'})
        
        # Date should be in GSI1SK but not in the main item since it wasn't provided
        assert 'date' not in item  # date field is not added to payload if not provided
        assert item['GSI1SK'].startswith(item['createdAt'])  # uses createdAt as default
    
    def test_create_strategy_item_basic(self):
        """Test create_strategy_item with basic data"""
        client = DynamoDBRepository()
        item = client.create_strategy_item('user-123', 'strat-456', {
            'name': 'Test Strategy',
            'market': 'ES',
            'timeframe': '5m',
            'dsl': {'rules': 'test'}
        })
        
        assert item['PK'] == 'USER#user-123'
        assert item['SK'] == 'STRAT#strat-456'
        assert item['GSI1PK'] == 'STRAT#user-123'
        assert item['entityType'] == 'STRATEGY'
        assert item['strategyId'] == 'strat-456'
        assert item['userId'] == 'user-123'
        assert item['name'] == 'Test Strategy'
        assert item['market'] == 'ES'
        assert item['timeframe'] == '5m'
        assert item['dsl'] == {'rules': 'test'}
        assert 'createdAt' in item
        assert 'updatedAt' in item
    
    def test_create_strategy_item_filters_allowed_fields(self):
        """Test create_strategy_item filters only allowed fields"""
        client = DynamoDBRepository()
        data = {
            'name': 'Test Strategy',
            'market': 'ES',
            'timeframe': '5m',
            'dsl': {'rules': 'test'},
            'invalid_field': 'should_be_filtered'
        }
        
        item = client.create_strategy_item('user-123', 'strat-456', data)
        
        # Check allowed fields are present
        for field in ALLOWED_STRATEGY_FIELDS:
            if field in data:
                assert item[field] == data[field]
        
        # Check invalid fields are filtered out
        assert 'invalid_field' not in item
    
    def test_create_strategy_item_filters_none_empty_values(self):
        """Test create_strategy_item filters None and empty values"""
        client = DynamoDBRepository()
        data = {
            'name': 'Test Strategy',
            'market': None,
            'timeframe': '',
            'dsl': {'rules': 'test'}
        }
        
        item = client.create_strategy_item('user-123', 'strat-456', data)
        
        assert item['name'] == 'Test Strategy'
        assert item['dsl'] == {'rules': 'test'}
        assert 'market' not in item
        assert 'timeframe' not in item
