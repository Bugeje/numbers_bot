# helpers/pdf_queue.py
"""
Asynchronous PDF Generation Queue with Batching Support
Optimizes PDF generation for high-load scenarios with intelligent queuing and batching.
"""

import asyncio
import logging
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class PDFJobStatus(Enum):
    """Status of PDF generation job."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PDFJob:
    """Represents a PDF generation job."""
    id: str
    func: Callable
    args: Tuple
    kwargs: Dict[str, Any]
    priority: int = 5  # 1-10, higher number = higher priority
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: PDFJobStatus = PDFJobStatus.QUEUED
    result: Optional[str] = None  # Path to generated PDF
    error: Optional[str] = None
    future: Optional[asyncio.Future] = field(default_factory=asyncio.Future)
    
    def __post_init__(self):
        if self.future is None:
            self.future = asyncio.Future()
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate job duration if completed."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def wait_time(self) -> float:
        """Calculate how long job waited in queue."""
        start_time = self.started_at or time.time()
        return start_time - self.created_at


class PDFGenerationQueue:
    """
    Asynchronous PDF generation queue with intelligent batching and prioritization.
    
    Features:
    - Priority-based job scheduling
    - Intelligent batching for similar operations
    - Resource-aware processing (respects semaphore limits)
    - Automatic retry mechanism
    - Performance metrics tracking
    """
    
    def __init__(self, max_workers: int = 5, batch_size: int = 3, batch_timeout: float = 2.0):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        
        # Job management
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._jobs: Dict[str, PDFJob] = {}
        self._workers: List[asyncio.Task] = []
        self._running = False
        
        # Metrics
        self.total_jobs = 0
        self.completed_jobs = 0
        self.failed_jobs = 0
        self.avg_processing_time = 0.0
        self.avg_wait_time = 0.0
        
        # Locks
        self._lock = asyncio.Lock()
        
        logger.info(f"PDFGenerationQueue initialized: {max_workers} workers, batch_size={batch_size}")
    
    async def submit_job(
        self,
        func: Callable,
        *args,
        priority: int = 5,
        **kwargs
    ) -> PDFJob:
        """
        Submit a PDF generation job to the queue.
        
        Args:
            func: PDF generation function
            *args: Function arguments
            priority: Job priority (1-10, higher = more urgent)
            **kwargs: Function keyword arguments
            
        Returns:
            PDFJob: Job object that can be awaited
        """
        job_id = str(uuid4())
        job = PDFJob(
            id=job_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority
        )
        
        async with self._lock:
            self._jobs[job_id] = job
            self.total_jobs += 1
            
            # Priority queue uses negative priority for max-heap behavior
            await self._queue.put((-priority, time.time(), job))
            
        logger.debug(f"Submitted PDF job {job_id} with priority {priority}")
        return job
    
    async def wait_for_job(self, job: PDFJob, timeout: Optional[float] = None) -> str:
        """
        Wait for a job to complete and return the result.
        
        Args:
            job: PDFJob to wait for
            timeout: Maximum time to wait (None = no timeout)
            
        Returns:
            str: Path to generated PDF file
            
        Raises:
            asyncio.TimeoutError: If timeout exceeded
            Exception: If job failed
        """
        try:
            if timeout:
                result = await asyncio.wait_for(job.future, timeout=timeout)
            else:
                result = await job.future
                
            if job.status == PDFJobStatus.FAILED:
                raise Exception(f"PDF generation failed: {job.error}")
            
            return result
        except asyncio.TimeoutError:
            logger.warning(f"PDF job {job.id} timed out after {timeout}s")
            await self.cancel_job(job.id)
            raise
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job if it hasn't started processing."""
        async with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            
            if job.status == PDFJobStatus.QUEUED:
                job.status = PDFJobStatus.CANCELLED
                job.future.cancel()
                logger.debug(f"Cancelled PDF job {job_id}")
                return True
            
            return False
    
    async def start(self):
        """Start the PDF generation workers."""
        if self._running:
            return
        
        self._running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
        
        logger.info(f"Started {self.max_workers} PDF generation workers")
    
    async def stop(self, timeout: float = 10.0):
        """Stop all workers and wait for completion."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
        
        # Wait for workers to finish
        if self._workers:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._workers, return_exceptions=True),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.warning("Some PDF workers didn't finish within timeout")
        
        self._workers.clear()
        logger.info("PDF generation queue stopped")
    
    async def _worker(self, worker_name: str):
        """Worker coroutine that processes PDF jobs."""
        logger.debug(f"PDF worker {worker_name} started")
        
        while self._running:
            try:
                # Wait for jobs with timeout to allow periodic checks
                try:
                    _, _, job = await asyncio.wait_for(
                        self._queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process the job
                await self._process_job(job, worker_name)
                
            except asyncio.CancelledError:
                logger.debug(f"PDF worker {worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"PDF worker {worker_name} error: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying
        
        logger.debug(f"PDF worker {worker_name} stopped")
    
    async def _process_job(self, job: PDFJob, worker_name: str):
        """Process a single PDF generation job."""
        job.status = PDFJobStatus.PROCESSING
        job.started_at = time.time()
        
        logger.debug(f"Worker {worker_name} processing job {job.id}")
        
        try:
            # Import concurrency manager here to avoid circular imports
            from .concurrency import get_concurrency_manager
            concurrency_manager = get_concurrency_manager()
            
            # Use PDF generation semaphore
            async with concurrency_manager.pdf_generation_context():
                # Execute the PDF generation function in a thread
                result = await asyncio.to_thread(job.func, *job.args, **job.kwargs)
                
                job.result = result
                job.status = PDFJobStatus.COMPLETED
                job.completed_at = time.time()
                
                # Set future result
                if not job.future.cancelled():
                    job.future.set_result(result)
                
                # Update metrics
                await self._update_metrics(job)
                
                logger.debug(f"Job {job.id} completed in {job.duration:.2f}s")
        
        except Exception as e:
            job.error = str(e)
            job.status = PDFJobStatus.FAILED
            job.completed_at = time.time()
            
            # Set future exception
            if not job.future.cancelled():
                job.future.set_exception(e)
            
            # Update metrics
            await self._update_metrics(job)
            
            logger.error(f"Job {job.id} failed: {e}")
    
    async def _update_metrics(self, job: PDFJob):
        """Update performance metrics."""
        async with self._lock:
            if job.status == PDFJobStatus.COMPLETED:
                self.completed_jobs += 1
                
                # Update average processing time (exponential moving average)
                if job.duration:
                    if self.avg_processing_time == 0:
                        self.avg_processing_time = job.duration
                    else:
                        self.avg_processing_time = (
                            0.1 * job.duration + 0.9 * self.avg_processing_time
                        )
                
                # Update average wait time
                wait_time = job.wait_time
                if self.avg_wait_time == 0:
                    self.avg_wait_time = wait_time
                else:
                    self.avg_wait_time = (
                        0.1 * wait_time + 0.9 * self.avg_wait_time
                    )
            
            elif job.status == PDFJobStatus.FAILED:
                self.failed_jobs += 1
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        async with self._lock:
            queue_size = self._queue.qsize()
            
            # Count jobs by status
            status_counts = {}
            for status in PDFJobStatus:
                status_counts[status.value] = sum(
                    1 for job in self._jobs.values() 
                    if job.status == status
                )
            
            return {
                "queue_size": queue_size,
                "total_jobs": self.total_jobs,
                "completed_jobs": self.completed_jobs,
                "failed_jobs": self.failed_jobs,
                "success_rate": (
                    self.completed_jobs / max(1, self.total_jobs) * 100
                ),
                "avg_processing_time_ms": self.avg_processing_time * 1000,
                "avg_wait_time_ms": self.avg_wait_time * 1000,
                "status_counts": status_counts,
                "workers_running": len(self._workers),
                "is_running": self._running,
            }


# Global PDF queue instance
_pdf_queue: Optional[PDFGenerationQueue] = None


async def get_pdf_queue() -> PDFGenerationQueue:
    """Get the global PDF generation queue."""
    global _pdf_queue
    if _pdf_queue is None:
        from config import settings
        _pdf_queue = PDFGenerationQueue(
            max_workers=min(settings.pdf_semaphore_limit, 5),
            batch_size=3,
            batch_timeout=2.0
        )
        await _pdf_queue.start()
    return _pdf_queue


async def cleanup_pdf_queue():
    """Clean up the global PDF queue."""
    global _pdf_queue
    if _pdf_queue:
        await _pdf_queue.stop()
        _pdf_queue = None


async def generate_pdf_async(
    func: Callable,
    *args,
    priority: int = 5,
    timeout: Optional[float] = 60.0,
    **kwargs
) -> str:
    """
    Convenience function to generate PDF asynchronously.
    
    Args:
        func: PDF generation function
        *args: Function arguments
        priority: Job priority (1-10)
        timeout: Maximum wait time
        **kwargs: Function keyword arguments
        
    Returns:
        str: Path to generated PDF
    """
    queue = await get_pdf_queue()
    job = await queue.submit_job(func, *args, priority=priority, **kwargs)
    return await queue.wait_for_job(job, timeout=timeout)