# helpers/concurrency.py
"""
Concurrency Control Manager for High Load Support
Provides semaphores and rate limiting for AI requests and PDF generation.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Optional, AsyncGenerator
from dataclasses import dataclass

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class OperationMetrics:
    """Metrics for tracking operation performance."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_duration: float = 0.0
    last_request_time: float = 0.0


class ConcurrencyManager:
    """
    Manages concurrent operations with semaphores and rate limiting.
    
    Features:
    - AI request concurrency control
    - PDF generation concurrency control  
    - Performance metrics tracking
    - Backpressure handling
    """
    
    def __init__(self):
        # Semaphores for different operation types
        self.ai_semaphore = asyncio.Semaphore(settings.ai_semaphore_limit)
        self.pdf_semaphore = asyncio.Semaphore(settings.pdf_semaphore_limit)
        
        # Metrics tracking
        self.metrics: Dict[str, OperationMetrics] = {
            'ai_requests': OperationMetrics(),
            'pdf_generation': OperationMetrics(),
        }
        
        # Rate limiting (per-minute tracking)
        self.rate_windows: Dict[str, list] = {
            'ai_requests': [],
            'pdf_generation': [],
        }
        
        self._lock = asyncio.Lock()
        logger.info(f"ConcurrencyManager initialized - AI: {settings.ai_semaphore_limit}, PDF: {settings.pdf_semaphore_limit}")
    
    async def _update_metrics(self, operation_type: str, duration: float, success: bool):
        """Update metrics for an operation."""
        async with self._lock:
            metrics = self.metrics[operation_type]
            metrics.total_requests += 1
            metrics.last_request_time = time.time()
            
            if success:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1
            
            # Update rolling average duration
            if metrics.total_requests == 1:
                metrics.avg_duration = duration
            else:
                # Exponential moving average with alpha=0.1
                metrics.avg_duration = 0.1 * duration + 0.9 * metrics.avg_duration
    
    async def _check_rate_limit(self, operation_type: str) -> bool:
        """Check if operation is within rate limits."""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        async with self._lock:
            # Clean old entries
            self.rate_windows[operation_type] = [
                t for t in self.rate_windows[operation_type] 
                if t > window_start
            ]
            
            # Check current rate
            current_rate = len(self.rate_windows[operation_type])
            if current_rate >= settings.security.rate_limit_per_minute:
                logger.warning(f"Rate limit exceeded for {operation_type}: {current_rate}/min")
                return False
            
            # Add current request
            self.rate_windows[operation_type].append(current_time)
            return True
    
    @asynccontextmanager
    async def ai_request_context(self) -> AsyncGenerator[None, None]:
        """Context manager for AI requests with concurrency control."""
        if not await self._check_rate_limit('ai_requests'):
            raise RuntimeError("AI request rate limit exceeded")
        
        start_time = time.time()
        success = False
        
        try:
            async with self.ai_semaphore:
                logger.debug(f"AI request started (available slots: {self.ai_semaphore._value})")
                yield
                success = True
        except Exception as e:
            logger.error(f"AI request failed: {e}")
            raise
        finally:
            duration = time.time() - start_time
            await self._update_metrics('ai_requests', duration, success)
            logger.debug(f"AI request completed in {duration:.2f}s (success: {success})")
    
    @asynccontextmanager
    async def pdf_generation_context(self) -> AsyncGenerator[None, None]:
        """Context manager for PDF generation with concurrency control."""
        if not await self._check_rate_limit('pdf_generation'):
            raise RuntimeError("PDF generation rate limit exceeded")
        
        start_time = time.time()
        success = False
        
        try:
            async with self.pdf_semaphore:
                logger.debug(f"PDF generation started (available slots: {self.pdf_semaphore._value})")
                yield
                success = True
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
        finally:
            duration = time.time() - start_time
            await self._update_metrics('pdf_generation', duration, success)
            logger.debug(f"PDF generation completed in {duration:.2f}s (success: {success})")
    
    async def get_metrics(self) -> Dict[str, dict]:
        """Get current performance metrics."""
        async with self._lock:
            return {
                operation_type: {
                    'total_requests': metrics.total_requests,
                    'successful_requests': metrics.successful_requests,
                    'failed_requests': metrics.failed_requests,
                    'success_rate': (
                        metrics.successful_requests / metrics.total_requests * 100
                        if metrics.total_requests > 0 else 0
                    ),
                    'avg_duration_ms': metrics.avg_duration * 1000,
                    'current_rate_per_minute': len(self.rate_windows[operation_type]),
                }
                for operation_type, metrics in self.metrics.items()
            }
    
    async def get_capacity_status(self) -> Dict[str, dict]:
        """Get current capacity and load status."""
        return {
            'ai_requests': {
                'available_slots': self.ai_semaphore._value,
                'total_slots': settings.ai_semaphore_limit,
                'utilization_percent': (
                    (settings.ai_semaphore_limit - self.ai_semaphore._value) / 
                    settings.ai_semaphore_limit * 100
                ),
            },
            'pdf_generation': {
                'available_slots': self.pdf_semaphore._value,
                'total_slots': settings.pdf_semaphore_limit,
                'utilization_percent': (
                    (settings.pdf_semaphore_limit - self.pdf_semaphore._value) / 
                    settings.pdf_semaphore_limit * 100
                ),
            }
        }
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on concurrency manager."""
        try:
            # Check semaphore availability
            ai_healthy = self.ai_semaphore._value > 0
            pdf_healthy = self.pdf_semaphore._value > 0
            
            # Check if metrics are being updated
            current_time = time.time()
            ai_recent = (
                current_time - self.metrics['ai_requests'].last_request_time < 300  # 5 minutes
                if self.metrics['ai_requests'].last_request_time > 0
                else True  # No requests yet is OK
            )
            pdf_recent = (
                current_time - self.metrics['pdf_generation'].last_request_time < 300
                if self.metrics['pdf_generation'].last_request_time > 0  
                else True
            )
            
            return {
                'ai_semaphore_healthy': ai_healthy,
                'pdf_semaphore_healthy': pdf_healthy,
                'ai_metrics_recent': ai_recent,
                'pdf_metrics_recent': pdf_recent,
                'overall_healthy': ai_healthy and pdf_healthy and ai_recent and pdf_recent,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {'overall_healthy': False, 'error': str(e)}


# Global concurrency manager instance
_concurrency_manager: Optional[ConcurrencyManager] = None


def get_concurrency_manager() -> ConcurrencyManager:
    """Get the global concurrency manager instance."""
    global _concurrency_manager
    if _concurrency_manager is None:
        _concurrency_manager = ConcurrencyManager()
    return _concurrency_manager