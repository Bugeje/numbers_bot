# helpers/memory_manager.py
"""
Memory Management and Resource Optimization
Handles temporary file cleanup, caching, and memory optimization for high-load scenarios.
"""

import asyncio
import gc
import logging
import os
import tempfile
import time
import weakref
from pathlib import Path
from typing import Any, Dict, Optional, Set
from dataclasses import dataclass
from threading import RLock

logger = logging.getLogger(__name__)


@dataclass
class ResourceInfo:
    """Information about a managed resource."""
    path: str
    created_at: float
    size_bytes: int
    access_count: int = 0
    last_accessed: float = 0.0
    
    def __post_init__(self):
        if self.last_accessed == 0.0:
            self.last_accessed = self.created_at


class MemoryManager:
    """
    Comprehensive memory management for the bot.
    
    Features:
    - Automatic temporary file cleanup
    - Memory usage monitoring  
    - Resource lifecycle management
    - Garbage collection optimization
    - Cache management with TTL
    """
    
    def __init__(self, cleanup_interval: float = 300.0, max_temp_age: float = 3600.0):
        self.cleanup_interval = cleanup_interval  # 5 minutes
        self.max_temp_age = max_temp_age  # 1 hour
        
        # Resource tracking
        self._temp_files: Dict[str, ResourceInfo] = {}
        self._permanent_files: Set[str] = set()
        self._cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, float] = {}
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Thread safety
        self._lock = RLock()
        
        # Weak reference tracking for automatic cleanup
        self._weak_refs: Set[weakref.ref] = set()
        
        logger.info(f"MemoryManager initialized: cleanup every {cleanup_interval}s, max temp age {max_temp_age}s")
    
    async def start(self):
        """Start the memory manager cleanup task."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("MemoryManager started")
    
    async def stop(self):
        """Stop the memory manager and clean up all resources."""
        if not self._running:
            return
        
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Final cleanup
        await self.cleanup_all()
        logger.info("MemoryManager stopped")
    
    def register_temp_file(self, file_path: str, auto_cleanup: bool = True) -> str:
        """
        Register a temporary file for management.
        
        Args:
            file_path: Path to the temporary file
            auto_cleanup: Whether to automatically clean up this file
            
        Returns:
            str: The registered file path
        """
        with self._lock:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                resource_info = ResourceInfo(
                    path=file_path,
                    created_at=time.time(),
                    size_bytes=stat.st_size
                )
                
                if auto_cleanup:
                    self._temp_files[file_path] = resource_info
                else:
                    self._permanent_files.add(file_path)
                
                logger.debug(f"Registered {'temp' if auto_cleanup else 'permanent'} file: {file_path} ({stat.st_size} bytes)")
        
        return file_path
    
    def access_file(self, file_path: str):
        """Mark a file as accessed for LRU tracking."""
        with self._lock:
            if file_path in self._temp_files:
                resource = self._temp_files[file_path]
                resource.access_count += 1
                resource.last_accessed = time.time()
    
    def unregister_file(self, file_path: str):
        """Unregister a file from management."""
        with self._lock:
            self._temp_files.pop(file_path, None)
            self._permanent_files.discard(file_path)
            logger.debug(f"Unregistered file: {file_path}")
    
    async def cleanup_temp_files(self, force_all: bool = False) -> int:
        """
        Clean up old temporary files.
        
        Args:
            force_all: If True, clean up all temp files regardless of age
            
        Returns:
            int: Number of files cleaned up
        """
        cleaned = 0
        current_time = time.time()
        
        with self._lock:
            files_to_remove = []
            
            for path, resource in self._temp_files.items():
                age = current_time - resource.created_at
                
                if force_all or age > self.max_temp_age:
                    try:
                        if os.path.exists(path):
                            os.unlink(path)
                            logger.debug(f"Cleaned up temp file: {path} (age: {age:.1f}s)")
                        files_to_remove.append(path)
                        cleaned += 1
                    except Exception as e:
                        logger.error(f"Failed to cleanup temp file {path}: {e}")
            
            # Remove from tracking
            for path in files_to_remove:
                del self._temp_files[path]
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} temporary files")
        
        return cleaned
    
    def set_cache(self, key: str, value: Any, ttl: float = 3600.0):
        """
        Set a value in the cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        with self._lock:
            self._cache[key] = value
            self._cache_ttl[key] = time.time() + ttl
            logger.debug(f"Cached value for key: {key} (TTL: {ttl}s)")
    
    def get_cache(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if expired/not found
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            # Check TTL
            if time.time() > self._cache_ttl[key]:
                del self._cache[key]
                del self._cache_ttl[key]
                logger.debug(f"Cache key expired: {key}")
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return self._cache[key]
    
    def clear_cache(self):
        """Clear all cached values."""
        with self._lock:
            cleared = len(self._cache)
            self._cache.clear()
            self._cache_ttl.clear()
            logger.info(f"Cleared {cleared} cache entries")
    
    async def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries."""
        current_time = time.time()
        expired = []
        
        with self._lock:
            for key, expiry_time in self._cache_ttl.items():
                if current_time > expiry_time:
                    expired.append(key)
            
            for key in expired:
                del self._cache[key]
                del self._cache_ttl[key]
        
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired cache entries")
        
        return len(expired)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        import psutil
        import sys
        
        # Process memory info
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Temporary files stats
        with self._lock:
            temp_files_count = len(self._temp_files)
            temp_files_size = sum(r.size_bytes for r in self._temp_files.values())
            
            cache_count = len(self._cache)
            cache_size = sys.getsizeof(self._cache)
            for value in self._cache.values():
                cache_size += sys.getsizeof(value)
        
        return {
            "process_memory_mb": memory_info.rss / 1024 / 1024,
            "process_memory_vms_mb": memory_info.vms / 1024 / 1024,
            "temp_files_count": temp_files_count,
            "temp_files_size_mb": temp_files_size / 1024 / 1024,
            "cache_entries": cache_count,
            "cache_size_mb": cache_size / 1024 / 1024,
            "gc_objects": len(gc.get_objects()),
        }
    
    async def force_garbage_collection(self):
        """Force garbage collection and log results."""
        before_objects = len(gc.get_objects())
        
        # Run garbage collection
        collected = gc.collect()
        
        after_objects = len(gc.get_objects())
        freed_objects = before_objects - after_objects
        
        logger.info(f"Garbage collection: collected {collected} objects, freed {freed_objects} objects")
        
        return {
            "collected": collected,
            "freed_objects": freed_objects,
            "remaining_objects": after_objects
        }
    
    async def cleanup_all(self):
        """Perform comprehensive cleanup of all managed resources."""
        logger.info("Starting comprehensive cleanup")
        
        # Clean up all temporary files
        await self.cleanup_temp_files(force_all=True)
        
        # Clear cache
        self.clear_cache()
        
        # Force garbage collection
        await self.force_garbage_collection()
        
        logger.info("Comprehensive cleanup completed")
    
    async def _cleanup_loop(self):
        """Main cleanup loop that runs periodically."""
        logger.debug("Memory cleanup loop started")
        
        while self._running:
            try:
                # Clean up old temp files
                await self.cleanup_temp_files()
                
                # Clean up expired cache entries
                await self.cleanup_expired_cache()
                
                # Force garbage collection every 10 cleanup cycles
                if hasattr(self, '_cleanup_count'):
                    self._cleanup_count += 1
                else:
                    self._cleanup_count = 1
                
                if self._cleanup_count % 10 == 0:
                    await self.force_garbage_collection()
                
                # Log memory stats periodically
                if self._cleanup_count % 5 == 0:
                    stats = self.get_memory_stats()
                    logger.info(f"Memory stats: {stats['process_memory_mb']:.1f}MB process, "
                              f"{stats['temp_files_count']} temp files ({stats['temp_files_size_mb']:.1f}MB), "
                              f"{stats['cache_entries']} cache entries")
                
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                logger.debug("Memory cleanup loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in memory cleanup loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
        
        logger.debug("Memory cleanup loop stopped")


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


async def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
        await _memory_manager.start()
    return _memory_manager


async def cleanup_memory_manager():
    """Clean up the global memory manager."""
    global _memory_manager
    if _memory_manager:
        await _memory_manager.stop()
        _memory_manager = None


def create_managed_temp_file(suffix: str = ".tmp", prefix: str = "bot_", auto_cleanup: bool = True) -> str:
    """
    Create a temporary file that will be automatically managed.
    
    Args:
        suffix: File suffix
        prefix: File prefix
        auto_cleanup: Whether to automatically clean up this file
        
    Returns:
        str: Path to the created temporary file
    """
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)  # Close the file descriptor, keep the file
    
    # Register with memory manager if available
    try:
        manager = asyncio.get_event_loop().run_until_complete(get_memory_manager())
        manager.register_temp_file(path, auto_cleanup=auto_cleanup)
    except Exception as e:
        logger.warning(f"Failed to register temp file with memory manager: {e}")
    
    return path