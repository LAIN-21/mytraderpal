"""Metrics collection for Prometheus monitoring."""
from typing import Dict, Any
from datetime import datetime, timezone


class MetricsCollector:
    """Simple metrics collector for request tracking."""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_latency_ms = 0.0
        self.start_time = datetime.now(timezone.utc)
    
    def record_request(self, latency_ms: float, is_error: bool = False):
        """Record a request with its latency."""
        self.request_count += 1
        self.total_latency_ms += latency_ms
        if is_error:
            self.error_count += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics in Prometheus-compatible format."""
        avg_latency = (
            self.total_latency_ms / self.request_count
            if self.request_count > 0
            else 0.0
        )
        
        uptime_seconds = (
            datetime.now(timezone.utc) - self.start_time
        ).total_seconds()
        
        return {
            'requests_total': self.request_count,
            'errors_total': self.error_count,
            'request_latency_seconds_avg': avg_latency / 1000.0,
            'uptime_seconds': uptime_seconds,
            'error_rate': (
                self.error_count / self.request_count
                if self.request_count > 0
                else 0.0
            )
        }
    
    def get_prometheus_format(self) -> str:
        """Get metrics in Prometheus text format."""
        metrics = self.get_metrics()
        lines = []
        
        for key, value in metrics.items():
            lines.append(f"# HELP {key} {key.replace('_', ' ').title()}")
            lines.append(f"# TYPE {key} gauge")
            lines.append(f"{key} {value}")
        
        return "\n".join(lines)


# Global metrics instance (shared across Lambda invocations in same container)
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _metrics


