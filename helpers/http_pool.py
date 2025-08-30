# helpers/http_pool.py
"""
HTTP Client Pool Manager for High Concurrency Support
Replaces single global httpx client with a pool of clients for better scalability.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)


class HTTPClientPool:
    """
    Manages a pool of HTTP clients for high-concurrency scenarios.
    
    Features:
    - Connection pooling with configurable limits
    - Automatic client rotation to prevent bottlenecks
    - Proper resource cleanup
    - Thread-safe operation
    """
    
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self._clients: list[httpx.AsyncClient] = []
        self._current_index = 0
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def _create_client(self) -> httpx.AsyncClient:
        """Create a new HTTP client with optimal settings."""
        limits = httpx.Limits(
            max_connections=settings.connection_pool_size // self.pool_size,
            max_keepalive_connections=settings.max_keepalive_connections // self.pool_size,
            keepalive_expiry=settings.keepalive_expiry
        )
        
        timeout = httpx.Timeout(
            connect=10.0,
            read=settings.http_timeout,
            write=30.0,
            pool=5.0
        )
        
        return httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            follow_redirects=True,
            http2=True  # Enable HTTP/2 for better performance
        )
    
    async def initialize(self):
        """Initialize the client pool."""
        if self._initialized:
            return
            
        async with self._lock:
            if self._initialized:
                return
                
            logger.info(f"Initializing HTTP client pool with {self.pool_size} clients")
            
            for i in range(self.pool_size):
                client = await self._create_client()
                self._clients.append(client)
                logger.debug(f"Created HTTP client {i+1}/{self.pool_size}")
            
            self._initialized = True
            logger.info("HTTP client pool initialized successfully")
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get the next client from the pool (round-robin)."""
        if not self._initialized:
            await self.initialize()
        
        async with self._lock:
            client = self._clients[self._current_index]
            self._current_index = (self._current_index + 1) % self.pool_size
            return client
    
    @asynccontextmanager
    async def client_context(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Context manager for getting a client with proper error handling."""
        client = await self.get_client()
        try:
            yield client
        except Exception as e:
            logger.error(f"Error in HTTP client context: {e}")
            raise
    
    async def cleanup(self):
        """Clean up all clients in the pool."""
        if not self._initialized:
            return
            
        async with self._lock:
            logger.info("Cleaning up HTTP client pool")
            
            for i, client in enumerate(self._clients):
                try:
                    await client.aclose()
                    logger.debug(f"Closed HTTP client {i+1}/{self.pool_size}")
                except Exception as e:
                    logger.error(f"Error closing HTTP client {i+1}: {e}")
            
            self._clients.clear()
            self._current_index = 0
            self._initialized = False
            logger.info("HTTP client pool cleanup completed")
    
    async def health_check(self) -> dict:
        """Perform health check on all clients."""
        if not self._initialized:
            return {"status": "not_initialized", "healthy_clients": 0, "total_clients": 0}
        
        healthy_count = 0
        total_count = len(self._clients)
        
        for i, client in enumerate(self._clients):
            try:
                # Simple health check - we could ping a lightweight endpoint
                if not client.is_closed:
                    healthy_count += 1
            except Exception as e:
                logger.warning(f"Health check failed for client {i+1}: {e}")
        
        return {
            "status": "healthy" if healthy_count == total_count else "degraded",
            "healthy_clients": healthy_count,
            "total_clients": total_count,
            "health_percentage": (healthy_count / total_count * 100) if total_count > 0 else 0
        }


# Global HTTP client pool instance
_http_pool: Optional[HTTPClientPool] = None


async def get_http_pool() -> HTTPClientPool:
    """Get the global HTTP client pool instance."""
    global _http_pool
    if _http_pool is None:
        _http_pool = HTTPClientPool(pool_size=5)  # Configurable via env in future
        await _http_pool.initialize()
    return _http_pool


async def cleanup_http_pool():
    """Clean up the global HTTP client pool."""
    global _http_pool
    if _http_pool:
        await _http_pool.cleanup()
        _http_pool = None