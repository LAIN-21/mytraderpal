#!/usr/bin/env python3
"""
Local testing script for Lambda handler.
Use this to test the backend without deploying.
"""
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.main import handler


def test_health():
    """Test health endpoint."""
    event = {
        'httpMethod': 'GET',
        'path': '/v1/health',
        'headers': {},
        'queryStringParameters': {}
    }
    
    result = handler(event, None)
    print("Health Check:")
    print(json.dumps(json.loads(result['body']), indent=2))
    print(f"Status: {result['statusCode']}\n")


def test_create_note():
    """Test creating a note."""
    event = {
        'httpMethod': 'POST',
        'path': '/v1/notes',
        'headers': {
            'X-MTP-Dev-User': 'test-user-123',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'text': 'Test note from local script',
            'date': '2025-01-15',
            'direction': 'LONG'
        }),
        'queryStringParameters': {}
    }
    
    # Set dev mode
    os.environ['DEV_MODE'] = 'true'
    os.environ['TABLE_NAME'] = 'mtp_app'
    
    result = handler(event, None)
    print("Create Note:")
    print(json.dumps(json.loads(result['body']), indent=2))
    print(f"Status: {result['statusCode']}\n")


if __name__ == '__main__':
    print("Testing Lambda Handler Locally\n")
    print("=" * 50 + "\n")
    
    # Test health (no auth required)
    test_health()
    
    # Test create note (requires dev mode)
    # Note: This will fail if DynamoDB is not accessible
    # For real testing, use mocks or deploy to AWS
    try:
        test_create_note()
    except Exception as e:
        print(f"Note: Create note test requires AWS DynamoDB or mocks")
        print(f"Error: {e}\n")
    
    print("=" * 50)
    print("Note: For full testing, use pytest with mocks:")
    print("  python -m pytest tests/unit/ -v")

