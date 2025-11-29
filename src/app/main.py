"""Lambda handler entry point for MyTraderPal API."""
from app.api.router import route_request


def handler(event, context):
    """
    AWS Lambda handler function.
    
    Routes API Gateway events to appropriate handlers.
    """
    return route_request(event)

