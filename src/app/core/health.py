"""Health check endpoint implementation."""
import os
from typing import Dict, Any
from datetime import datetime, timezone

from app.core.metrics import get_metrics


def get_health_status() -> Dict[str, Any]:
    """
    Get comprehensive health status including:
    - Basic health status
    - Database connectivity (if applicable)
    - Metrics summary
    """
    metrics = get_metrics()
    metrics_data = metrics.get_metrics()
    
    # Check environment variables
    table_name = os.getenv('TABLE_NAME', 'not_set')
    dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0',
        'environment': {
            'table_name_configured': table_name != 'not_set',
            'dev_mode': dev_mode
        },
        'metrics': {
            'requests_total': metrics_data['requests_total'],
            'errors_total': metrics_data['errors_total'],
            'error_rate': round(metrics_data['error_rate'], 4),
            'avg_latency_ms': round(metrics_data['request_latency_seconds_avg'] * 1000, 2),
            'uptime_seconds': int(metrics_data['uptime_seconds'])
        }
    }
    
    # Determine overall health
    if metrics_data['error_rate'] > 0.5:  # More than 50% errors
        health_status['status'] = 'degraded'
    
    return health_status


