from services.api.common.dynamodb import DynamoDBClient

def test_create_note_item_shapes_keys(monkeypatch):
    monkeypatch.setenv('TABLE_NAME', 'dummy')
    client = DynamoDBClient()
    item = client.create_note_item('u1', 'note-1', {'text': 'hi', 'date': '2025-01-01T00:00:00Z'})
    assert item['PK'] == 'USER#u1'
    assert item['SK'] == 'NOTE#note-1'
    assert item['GSI1PK'] == 'NOTE#u1'
    assert item['GSI1SK'].startswith('2025-01-01T00:00:00Z#')
    assert item['entityType'] == 'NOTE'
    assert item['text'] == 'hi'

def test_create_strategy_item_shapes_keys(monkeypatch):
    monkeypatch.setenv('TABLE_NAME', 'dummy')
    client = DynamoDBClient()
    item = client.create_strategy_item('u1', 'strat-1', {'name': 'S'})
    assert item['PK'] == 'USER#u1'
    assert item['SK'] == 'STRAT#strat-1'
    assert item['GSI1PK'] == 'STRAT#u1'
    assert item['entityType'] == 'STRATEGY'
    assert item['name'] == 'S'
