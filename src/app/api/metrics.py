"""Metrics API controller."""
from typing import Dict, Any

from app.core.metrics import get_metrics
from app.core.response import get_origin


def get_metrics_endpoint(event: Dict[str, Any]) -> Dict[str, Any]:
    """Expose metrics in Prometheus format."""
    metrics = get_metrics()
    prometheus_text = metrics.get_prometheus_format()
    
    # Return as plain text for Prometheus
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain; version=0.0.4',
            'Access-Control-Allow-Origin': get_origin(event),
        },
        'body': prometheus_text
    }


