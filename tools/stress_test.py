#!/usr/bin/env python3
"""
Stress Testing Tools for Numbers Bot
Simulates high load with multiple concurrent users to validate performance optimizations.
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from helpers.concurrency import get_concurrency_manager
from helpers.memory_manager import get_memory_manager
from helpers.monitoring import get_performance_monitor
from helpers.http_pool import get_http_pool

logger = logging.getLogger(__name__)


@dataclass
class UserSimulation:
    """Represents a simulated user session."""
    user_id: int
    name: str
    birthdate: str
    start_time: float
    actions_completed: int = 0
    errors_encountered: int = 0
    total_response_time: float = 0.0
    last_action_time: float = 0.0
    session_active: bool = True


@dataclass
class StressTestResults:
    """Results from a stress test run."""
    test_duration: float
    total_users: int
    concurrent_peak: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    max_response_time: float
    requests_per_second: float
    errors_by_type: Dict[str, int]
    memory_peak_mb: float
    memory_final_mb: float


class BotStressTester:
    """
    Comprehensive stress testing framework for the numbers bot.
    
    Features:
    - Simulates realistic user behavior patterns
    - Tests all major bot features (AI analysis, PDF generation)
    - Monitors system resources during tests
    - Generates detailed performance reports
    - Validates concurrency optimizations
    """
    
    def __init__(self, max_users: int = 100, test_duration: int = 300):
        self.max_users = max_users
        self.test_duration = test_duration  # 5 minutes default
        
        # Test state
        self.users: List[UserSimulation] = []
        self.active_users: int = 0
        self.response_times: List[float] = []
        self.errors: Dict[str, int] = {}
        self.start_time: float = 0
        self.peak_concurrent: int = 0
        
        # User scenarios
        self.scenarios = [
            self._scenario_core_analysis,
            self._scenario_extended_analysis,
            self._scenario_bridges_analysis,
            self._scenario_cycles_analysis,
            self._scenario_partner_analysis,
        ]
        
        # Test data
        self.test_names = [
            "Александр", "Мария", "Дмитрий", "Елена", "Сергей", "Анна",
            "Андрей", "Ольга", "Николай", "Татьяна", "Максим", "Ирина",
            "Владимир", "Наталья", "Алексей", "Екатерина", "Михаил", "Светлана"
        ]
        
        logger.info(f"StressTester initialized: {max_users} users, {test_duration}s duration")
    
    def _generate_random_birthdate(self) -> str:
        """Generate a random birthdate in DD.MM.YYYY format."""
        start_date = datetime(1950, 1, 1)
        end_date = datetime(2005, 12, 31)
        
        random_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        return random_date.strftime("%d.%m.%Y")
    
    def _create_user(self, user_id: int) -> UserSimulation:
        """Create a simulated user."""
        return UserSimulation(
            user_id=user_id,
            name=random.choice(self.test_names),
            birthdate=self._generate_random_birthdate(),
            start_time=time.time()
        )
    
    async def _scenario_core_analysis(self, user: UserSimulation) -> Tuple[bool, float]:
        """Simulate core profile analysis scenario."""
        start_time = time.time()
        
        try:
            # Simulate calculations and AI analysis
            from calc import calculate_core_profile
            from intelligence import get_ai_analysis
            
            with get_concurrency_manager().ai_request_context():
                profile = calculate_core_profile(user.name, user.birthdate)
                analysis = await get_ai_analysis(profile)
                
                # Simulate PDF generation
                await asyncio.sleep(random.uniform(0.5, 2.0))  # PDF generation time
            
            return True, time.time() - start_time
            
        except Exception as e:
            logger.error(f"Core analysis failed for user {user.user_id}: {e}")
            return False, time.time() - start_time
    
    async def _scenario_extended_analysis(self, user: UserSimulation) -> Tuple[bool, float]:
        """Simulate extended analysis scenario."""
        start_time = time.time()
        
        try:
            from calc.extended import calculate_extended_profile
            from intelligence import get_extended_analysis
            
            with get_concurrency_manager().ai_request_context():
                profile = calculate_extended_profile(user.name, user.birthdate)
                analysis = await get_extended_analysis(profile)
                
                await asyncio.sleep(random.uniform(1.0, 3.0))
            
            return True, time.time() - start_time
            
        except Exception as e:
            logger.error(f"Extended analysis failed for user {user.user_id}: {e}")
            return False, time.time() - start_time
    
    async def _scenario_bridges_analysis(self, user: UserSimulation) -> Tuple[bool, float]:
        """Simulate bridges analysis scenario."""
        start_time = time.time()
        
        try:
            from calc.extended import calculate_bridges
            from intelligence import get_bridges_analysis
            
            with get_concurrency_manager().ai_request_context():
                bridges = calculate_bridges(user.name, user.birthdate)
                analysis = await get_bridges_analysis(bridges)
                
                await asyncio.sleep(random.uniform(0.8, 2.5))
            
            return True, time.time() - start_time
            
        except Exception as e:
            logger.error(f"Bridges analysis failed for user {user.user_id}: {e}")
            return False, time.time() - start_time
    
    async def _scenario_cycles_analysis(self, user: UserSimulation) -> Tuple[bool, float]:
        """Simulate cycles analysis scenario."""
        start_time = time.time()
        
        try:
            from calc.cycles import generate_personal_year_table, calculate_pinnacles_with_periods
            from intelligence import get_cycles_analysis
            from calc import calculate_core_profile
            
            with get_concurrency_manager().ai_request_context():
                profile = calculate_core_profile(user.name, user.birthdate)
                personal_years = generate_personal_year_table(user.birthdate)
                pinnacles = calculate_pinnacles_with_periods(user.birthdate, profile['life_path'])
                
                analysis = await get_cycles_analysis(
                    user.name, user.birthdate, str(profile['life_path']),
                    personal_years, pinnacles, {}
                )
                
                await asyncio.sleep(random.uniform(1.5, 4.0))
            
            return True, time.time() - start_time
            
        except Exception as e:
            logger.error(f"Cycles analysis failed for user {user.user_id}: {e}")
            return False, time.time() - start_time
    
    async def _scenario_partner_analysis(self, user: UserSimulation) -> Tuple[bool, float]:
        """Simulate partner compatibility analysis scenario."""
        start_time = time.time()
        
        try:
            from calc.extended import calculate_compatibility
            from intelligence import get_compatibility_interpretation
            from calc import calculate_core_profile
            
            # Create partner data
            partner_name = random.choice(self.test_names)
            partner_birthdate = self._generate_random_birthdate()
            
            with get_concurrency_manager().ai_request_context():
                profile_a = calculate_core_profile(user.name, user.birthdate)
                profile_b = calculate_core_profile(partner_name, partner_birthdate)
                
                compatibility = calculate_compatibility(profile_a, profile_b)
                analysis = await get_compatibility_interpretation(profile_a, profile_b)
                
                await asyncio.sleep(random.uniform(1.0, 3.5))
            
            return True, time.time() - start_time
            
        except Exception as e:
            logger.error(f"Partner analysis failed for user {user.user_id}: {e}")
            return False, time.time() - start_time
    
    async def _simulate_user_session(self, user: UserSimulation):
        """Simulate a complete user session."""
        logger.debug(f"Starting session for user {user.user_id}")
        
        while user.session_active and (time.time() - self.start_time) < self.test_duration:
            try:
                # Choose random scenario
                scenario = random.choice(self.scenarios)
                
                # Execute scenario
                success, response_time = await scenario(user)
                
                # Update user stats
                user.actions_completed += 1
                user.total_response_time += response_time
                user.last_action_time = time.time()
                
                # Record global stats
                self.response_times.append(response_time)
                
                if not success:
                    user.errors_encountered += 1
                    error_type = scenario.__name__
                    self.errors[error_type] = self.errors.get(error_type, 0) + 1
                
                # Wait before next action (simulate user thinking time)
                await asyncio.sleep(random.uniform(2.0, 10.0))
                
            except Exception as e:
                logger.error(f"Error in user {user.user_id} session: {e}")
                user.errors_encountered += 1
                await asyncio.sleep(1.0)
        
        user.session_active = False
        self.active_users -= 1
        logger.debug(f"Session ended for user {user.user_id}")
    
    async def _ramp_up_users(self):
        """Gradually ramp up user load."""
        ramp_duration = min(60, self.test_duration // 4)  # 25% of test duration for ramp-up
        users_per_second = self.max_users / ramp_duration
        
        logger.info(f"Ramping up {self.max_users} users over {ramp_duration}s")
        
        for i in range(self.max_users):
            user = self._create_user(i)
            self.users.append(user)
            
            # Start user session
            asyncio.create_task(self._simulate_user_session(user))
            self.active_users += 1
            
            # Update peak concurrent users
            if self.active_users > self.peak_concurrent:
                self.peak_concurrent = self.active_users
            
            # Control ramp-up rate
            if i < self.max_users - 1:  # Don't sleep after last user
                await asyncio.sleep(1.0 / users_per_second)
    
    async def _monitor_resources(self):
        """Monitor system resources during the test."""
        logger.info("Starting resource monitoring")
        
        memory_manager = await get_memory_manager()
        performance_monitor = await get_performance_monitor()
        
        peak_memory = 0.0
        
        while (time.time() - self.start_time) < self.test_duration:
            try:
                # Get memory stats
                memory_stats = memory_manager.get_memory_stats()
                current_memory = memory_stats['process_memory_mb']
                
                if current_memory > peak_memory:
                    peak_memory = current_memory
                
                # Log resource usage
                logger.info(f"Active users: {self.active_users}, "
                          f"Memory: {current_memory:.1f}MB, "
                          f"Completed requests: {len(self.response_times)}")
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                await asyncio.sleep(5)
        
        return peak_memory
    
    async def run_test(self) -> StressTestResults:
        """Run the complete stress test."""
        logger.info(f"Starting stress test: {self.max_users} users, {self.test_duration}s")
        
        self.start_time = time.time()
        
        try:
            # Start monitoring
            monitor_task = asyncio.create_task(self._monitor_resources())
            
            # Ramp up users
            await self._ramp_up_users()
            
            # Wait for test completion
            remaining_time = self.test_duration - (time.time() - self.start_time)
            if remaining_time > 0:
                logger.info(f"Test running... {remaining_time:.0f}s remaining")
                await asyncio.sleep(remaining_time)
            
            # Wait for monitoring to complete
            try:
                peak_memory = await asyncio.wait_for(monitor_task, timeout=10)
            except asyncio.TimeoutError:
                peak_memory = 0.0
                logger.warning("Resource monitoring timeout")
            
            # Calculate final memory
            memory_manager = await get_memory_manager()
            final_memory = memory_manager.get_memory_stats()['process_memory_mb']
            
            # Generate results
            return self._generate_results(peak_memory, final_memory)
            
        except Exception as e:
            logger.error(f"Stress test failed: {e}")
            raise
    
    def _generate_results(self, peak_memory: float, final_memory: float) -> StressTestResults:
        """Generate test results summary."""
        test_duration = time.time() - self.start_time
        
        total_requests = len(self.response_times)
        failed_requests = sum(self.errors.values())
        successful_requests = total_requests - failed_requests
        
        # Calculate percentiles
        if self.response_times:
            sorted_times = sorted(self.response_times)
            avg_response_time = sum(self.response_times) / len(self.response_times)
            p95_response_time = self._percentile(sorted_times, 95)
            p99_response_time = self._percentile(sorted_times, 99)
            max_response_time = max(self.response_times)
        else:
            avg_response_time = p95_response_time = p99_response_time = max_response_time = 0.0
        
        requests_per_second = total_requests / test_duration if test_duration > 0 else 0
        
        return StressTestResults(
            test_duration=test_duration,
            total_users=len(self.users),
            concurrent_peak=self.peak_concurrent,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            max_response_time=max_response_time,
            requests_per_second=requests_per_second,
            errors_by_type=dict(self.errors),
            memory_peak_mb=peak_memory,
            memory_final_mb=final_memory
        )
    
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


def print_results(results: StressTestResults):
    """Print formatted test results."""
    print("\n" + "="*80)
    print("🚀 STRESS TEST RESULTS")
    print("="*80)
    
    print(f"📊 Test Overview:")
    print(f"  Duration: {results.test_duration:.1f}s")
    print(f"  Total Users: {results.total_users}")
    print(f"  Peak Concurrent: {results.concurrent_peak}")
    print(f"  Requests/sec: {results.requests_per_second:.2f}")
    
    print(f"\n📈 Request Statistics:")
    print(f"  Total Requests: {results.total_requests}")
    print(f"  Successful: {results.successful_requests} ({results.successful_requests/max(1,results.total_requests)*100:.1f}%)")
    print(f"  Failed: {results.failed_requests} ({results.failed_requests/max(1,results.total_requests)*100:.1f}%)")
    
    print(f"\n⏱️  Response Times:")
    print(f"  Average: {results.avg_response_time*1000:.0f}ms")
    print(f"  95th percentile: {results.p95_response_time*1000:.0f}ms")
    print(f"  99th percentile: {results.p99_response_time*1000:.0f}ms")
    print(f"  Maximum: {results.max_response_time*1000:.0f}ms")
    
    print(f"\n💾 Memory Usage:")
    print(f"  Peak: {results.memory_peak_mb:.1f}MB")
    print(f"  Final: {results.memory_final_mb:.1f}MB")
    print(f"  Growth: {results.memory_final_mb - results.memory_peak_mb:.1f}MB")
    
    if results.errors_by_type:
        print(f"\n❌ Errors by Type:")
        for error_type, count in results.errors_by_type.items():
            print(f"  {error_type}: {count}")
    
    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    if results.requests_per_second > 10:
        print("  ✅ Excellent throughput")
    elif results.requests_per_second > 5:
        print("  ⚠️  Good throughput")
    else:
        print("  ❌ Low throughput - needs optimization")
    
    if results.avg_response_time < 2.0:
        print("  ✅ Excellent response times")
    elif results.avg_response_time < 5.0:
        print("  ⚠️  Good response times")
    else:
        print("  ❌ Slow response times - needs optimization")
    
    error_rate = results.failed_requests / max(1, results.total_requests) * 100
    if error_rate < 1.0:
        print("  ✅ Excellent reliability")
    elif error_rate < 5.0:
        print("  ⚠️  Good reliability")
    else:
        print("  ❌ Poor reliability - needs investigation")
    
    print("="*80)


async def main():
    """Main stress test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Numbers Bot Stress Test")
    parser.add_argument("--users", type=int, default=100, help="Number of concurrent users")
    parser.add_argument("--duration", type=int, default=300, help="Test duration in seconds")
    parser.add_argument("--output", type=str, help="Output file for results (JSON)")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run stress test
    tester = BotStressTester(max_users=args.users, test_duration=args.duration)
    
    try:
        results = await tester.run_test()
        
        # Print results
        print_results(results)
        
        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results.__dict__, f, indent=2)
            print(f"\n📁 Results saved to: {args.output}")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())