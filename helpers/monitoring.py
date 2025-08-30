# helpers/monitoring.py
"""
Performance Monitoring and Metrics Collection
Provides comprehensive monitoring for bot performance under high load.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """A single metric data point."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'value': self.value,
            'labels': self.labels,
            'datetime': datetime.fromtimestamp(self.timestamp, timezone.utc).isoformat()
        }


@dataclass
class PerformanceStats:
    """Performance statistics for a specific component."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    current_load: int = 0
    peak_load: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100


class MetricsCollector:
    """
    Collects and aggregates performance metrics.
    
    Features:
    - Real-time metrics collection
    - Histogram-based percentile calculations
    - Time-windowed aggregations
    - Export capabilities
    - Performance alerts
    """
    
    def __init__(self, max_points: int = 10000, window_size: int = 300):
        self.max_points = max_points
        self.window_size = window_size  # 5 minutes
        
        # Metric storage
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Component stats
        self._component_stats: Dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        
        # Alert thresholds
        self._alert_thresholds: Dict[str, Dict[str, float]] = {}
        self._alert_callbacks: List[Callable] = []
        
        logger.info(f"MetricsCollector initialized: max_points={max_points}, window_size={window_size}s")
    
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric value."""
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            labels=labels or {}
        )
        self._metrics[name].append(point)
        logger.debug(f"Recorded metric {name}: {value}")
    
    def increment_counter(self, name: str, amount: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        key = self._make_key(name, labels)
        self._counters[key] += amount
        self.record_metric(f"{name}_total", self._counters[key], labels)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value."""
        key = self._make_key(name, labels)
        self._gauges[key] = value
        self.record_metric(name, value, labels)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a value in a histogram for percentile calculations."""
        key = self._make_key(name, labels)
        self._histograms[key].append(value)
        self.record_metric(f"{name}_histogram", value, labels)
    
    def time_operation(self, component: str):
        """Context manager for timing operations."""
        return OperationTimer(self, component)
    
    def update_component_stats(
        self,
        component: str,
        success: bool,
        response_time: float,
        current_load: int = 0
    ):
        """Update performance statistics for a component."""
        stats = self._component_stats[component]
        
        stats.total_requests += 1
        if success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
        
        # Update response time statistics
        if response_time < stats.min_response_time:
            stats.min_response_time = response_time
        if response_time > stats.max_response_time:
            stats.max_response_time = response_time
        
        # Exponential moving average for avg response time
        if stats.avg_response_time == 0:
            stats.avg_response_time = response_time
        else:
            stats.avg_response_time = 0.1 * response_time + 0.9 * stats.avg_response_time
        
        # Update load tracking
        stats.current_load = current_load
        if current_load > stats.peak_load:
            stats.peak_load = current_load
        
        # Record histogram for percentiles
        self.record_histogram(f"{component}_response_time", response_time)
        
        # Update percentiles
        self._update_percentiles(component)
        
        # Check alerts
        self._check_alerts(component, stats)
    
    def _update_percentiles(self, component: str):
        """Update percentile calculations for a component."""
        hist_key = self._make_key(f"{component}_response_time", {})
        if hist_key in self._histograms and self._histograms[hist_key]:
            values = sorted(self._histograms[hist_key])
            
            stats = self._component_stats[component]
            stats.p95_response_time = self._percentile(values, 95)
            stats.p99_response_time = self._percentile(values, 99)
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile from sorted values."""
        if not values:
            return 0.0
        
        k = (len(values) - 1) * percentile / 100
        f = int(k)
        c = k - f
        
        if f + 1 < len(values):
            return values[f] * (1 - c) + values[f + 1] * c
        else:
            return values[f]
    
    def set_alert_threshold(self, component: str, metric: str, threshold: float):
        """Set an alert threshold for a component metric."""
        if component not in self._alert_thresholds:
            self._alert_thresholds[component] = {}
        self._alert_thresholds[component][metric] = threshold
        logger.info(f"Set alert threshold for {component}.{metric}: {threshold}")
    
    def add_alert_callback(self, callback: Callable):
        """Add a callback function for alerts."""
        self._alert_callbacks.append(callback)
    
    def _check_alerts(self, component: str, stats: PerformanceStats):
        """Check if any alert thresholds are exceeded."""
        if component not in self._alert_thresholds:
            return
        
        thresholds = self._alert_thresholds[component]
        alerts = []
        
        # Check various metrics
        checks = {
            'error_rate': stats.error_rate,
            'avg_response_time': stats.avg_response_time * 1000,  # Convert to ms
            'p95_response_time': stats.p95_response_time * 1000,
            'p99_response_time': stats.p99_response_time * 1000,
            'current_load': stats.current_load,
        }
        
        for metric, value in checks.items():
            if metric in thresholds and value > thresholds[metric]:
                alerts.append({
                    'component': component,
                    'metric': metric,
                    'value': value,
                    'threshold': thresholds[metric],
                    'timestamp': time.time()
                })
        
        # Trigger alert callbacks
        for alert in alerts:
            logger.warning(f"ALERT: {component}.{alert['metric']} = {alert['value']:.2f} > {alert['threshold']}")
            for callback in self._alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback error: {e}")
    
    def get_component_stats(self, component: str) -> Dict[str, Any]:
        """Get performance statistics for a component."""
        stats = self._component_stats[component]
        return asdict(stats)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all components."""
        return {
            component: asdict(stats)
            for component, stats in self._component_stats.items()
        }
    
    def get_metrics_window(self, name: str, seconds: int = None) -> List[Dict[str, Any]]:
        """Get metrics within a time window."""
        if seconds is None:
            seconds = self.window_size
        
        cutoff_time = time.time() - seconds
        
        if name not in self._metrics:
            return []
        
        return [
            point.to_dict()
            for point in self._metrics[name]
            if point.timestamp >= cutoff_time
        ]
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export all metrics in specified format."""
        if format.lower() == 'json':
            data = {
                'export_time': datetime.now(timezone.utc).isoformat(),
                'component_stats': self.get_all_stats(),
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'recent_metrics': {
                    name: self.get_metrics_window(name, 3600)  # Last hour
                    for name in self._metrics.keys()
                }
            }
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def save_metrics(self, file_path: str):
        """Save metrics to a file."""
        data = self.export_metrics('json')
        Path(file_path).write_text(data)
        logger.info(f"Metrics saved to {file_path}")
    
    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create a key for label-based metrics."""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}:{label_str}"


class OperationTimer:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, component: str):
        self.collector = collector
        self.component = component
        self.start_time = None
        self.success = True
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            
            # Determine if operation was successful
            success = exc_type is None and self.success
            
            # Record metrics
            self.collector.record_metric(f"{self.component}_duration", duration)
            self.collector.increment_counter(f"{self.component}_requests")
            if success:
                self.collector.increment_counter(f"{self.component}_success")
            else:
                self.collector.increment_counter(f"{self.component}_errors")
            
            # Update component stats (we don't have current_load here)
            self.collector.update_component_stats(self.component, success, duration)
    
    def mark_failure(self):
        """Mark this operation as failed."""
        self.success = False


class PerformanceMonitor:
    """
    High-level performance monitoring system.
    
    Integrates with all bot components to provide comprehensive monitoring.
    """
    
    def __init__(self, save_interval: float = 600.0):
        self.save_interval = save_interval
        self.collector = MetricsCollector()
        
        # Monitoring task
        self._monitor_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Set default alert thresholds
        self._setup_default_alerts()
        
        logger.info("PerformanceMonitor initialized")
    
    def _setup_default_alerts(self):
        """Set up default alert thresholds."""
        # AI component alerts
        self.collector.set_alert_threshold('ai_requests', 'error_rate', 10.0)  # 10% error rate
        self.collector.set_alert_threshold('ai_requests', 'avg_response_time', 30000)  # 30s avg
        self.collector.set_alert_threshold('ai_requests', 'p95_response_time', 45000)  # 45s p95
        
        # PDF generation alerts
        self.collector.set_alert_threshold('pdf_generation', 'error_rate', 5.0)  # 5% error rate
        self.collector.set_alert_threshold('pdf_generation', 'avg_response_time', 10000)  # 10s avg
        self.collector.set_alert_threshold('pdf_generation', 'current_load', 25)  # 25 concurrent
        
        # Memory alerts
        self.collector.set_alert_threshold('memory', 'process_memory_mb', 1024)  # 1GB RAM
        self.collector.set_alert_threshold('memory', 'temp_files_count', 100)  # 100 temp files
    
    async def start(self):
        """Start the performance monitor."""
        if self._running:
            return
        
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("PerformanceMonitor started")
    
    async def stop(self):
        """Stop the performance monitor."""
        if not self._running:
            return
        
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("PerformanceMonitor stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        logger.debug("Performance monitoring loop started")
        
        while self._running:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Save metrics periodically
                if hasattr(self, '_save_counter'):
                    self._save_counter += 1
                else:
                    self._save_counter = 1
                
                if self._save_counter % 10 == 0:  # Every 10 cycles
                    try:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        self.collector.save_metrics(f"metrics_{timestamp}.json")
                    except Exception as e:
                        logger.error(f"Failed to save metrics: {e}")
                
                await asyncio.sleep(self.save_interval / 10)  # Check every minute
                
            except asyncio.CancelledError:
                logger.debug("Performance monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(5)
        
        logger.debug("Performance monitoring loop stopped")
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            # Memory metrics
            from .memory_manager import get_memory_manager
            memory_manager = await get_memory_manager()
            memory_stats = memory_manager.get_memory_stats()
            
            for metric, value in memory_stats.items():
                self.collector.set_gauge(f"memory_{metric}", value)
            
            # Concurrency metrics
            from .concurrency import get_concurrency_manager
            concurrency_manager = get_concurrency_manager()
            capacity_status = await concurrency_manager.get_capacity_status()
            
            for component, status in capacity_status.items():
                for metric, value in status.items():
                    self.collector.set_gauge(f"concurrency_{component}_{metric}", value)
            
            # HTTP pool metrics
            from .http_pool import get_http_pool
            http_pool = await get_http_pool()
            health = await http_pool.health_check()
            
            self.collector.set_gauge("http_pool_health_percentage", health["health_percentage"])
            self.collector.set_gauge("http_pool_healthy_clients", health["healthy_clients"])
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for performance dashboard."""
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'component_stats': self.collector.get_all_stats(),
            'system_metrics': {
                'memory': self.collector.get_metrics_window('memory_process_memory_mb', 300),
                'concurrency': {
                    'ai_utilization': self.collector.get_metrics_window('concurrency_ai_requests_utilization_percent', 300),
                    'pdf_utilization': self.collector.get_metrics_window('concurrency_pdf_generation_utilization_percent', 300),
                },
                'http_pool': self.collector.get_metrics_window('http_pool_health_percentage', 300),
            }
        }


# Global monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


async def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
        await _performance_monitor.start()
    return _performance_monitor


async def cleanup_performance_monitor():
    """Clean up the global performance monitor."""
    global _performance_monitor
    if _performance_monitor:
        await _performance_monitor.stop()
        _performance_monitor = None