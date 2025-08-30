#!/usr/bin/env python3
"""
Performance Dashboard for Numbers Bot
Real-time monitoring and analysis of bot performance metrics.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.monitoring import get_performance_monitor
from helpers.concurrency import get_concurrency_manager
from helpers.memory_manager import get_memory_manager
from helpers.http_pool import get_http_pool


class PerformanceDashboard:
    """Real-time performance dashboard."""
    
    def __init__(self, refresh_interval: float = 5.0):
        self.refresh_interval = refresh_interval
        self.running = False
    
    async def start(self):
        """Start the dashboard."""
        print("🚀 Starting Performance Dashboard...")
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        
        try:
            while self.running:
                await self._display_dashboard()
                await asyncio.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped")
        finally:
            self.running = False
    
    async def _display_dashboard(self):
        """Display the current dashboard."""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Header
        print("="*80)
        print(f"📊 NUMBERS BOT PERFORMANCE DASHBOARD - {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)
        
        try:
            # Get all managers
            monitor = await get_performance_monitor()
            concurrency_mgr = get_concurrency_manager()
            memory_mgr = await get_memory_manager()
            http_pool = await get_http_pool()
            
            # Display metrics
            await self._display_system_overview(memory_mgr, http_pool)
            await self._display_concurrency_status(concurrency_mgr)
            await self._display_component_performance(monitor)
            await self._display_alerts()
            
        except Exception as e:
            print(f"❌ Error fetching metrics: {e}")
        
        print("="*80)
        print(f"🔄 Refreshing every {self.refresh_interval}s | Press Ctrl+C to stop")
    
    async def _display_system_overview(self, memory_mgr, http_pool):
        """Display system overview metrics."""
        print("🖥️  SYSTEM OVERVIEW")
        print("-" * 40)
        
        # Memory stats
        memory_stats = memory_mgr.get_memory_stats()
        print(f"Memory Usage: {memory_stats['process_memory_mb']:.1f}MB")
        print(f"Temp Files: {memory_stats['temp_files_count']} ({memory_stats['temp_files_size_mb']:.1f}MB)")
        print(f"Cache Entries: {memory_stats['cache_entries']}")
        
        # HTTP pool health
        pool_health = await http_pool.health_check()
        health_icon = "✅" if pool_health['status'] == 'healthy' else "⚠️"
        print(f"HTTP Pool: {health_icon} {pool_health['healthy_clients']}/{pool_health['total_clients']} clients")
        print()
    
    async def _display_concurrency_status(self, concurrency_mgr):
        """Display concurrency status."""
        print("⚡ CONCURRENCY STATUS")
        print("-" * 40)
        
        capacity = await concurrency_mgr.get_capacity_status()
        metrics = await concurrency_mgr.get_metrics()
        
        for component in ['ai_requests', 'pdf_generation']:
            if component in capacity:
                cap = capacity[component]
                met = metrics.get(component, {})
                
                utilization = cap['utilization_percent']
                util_icon = "🔴" if utilization > 80 else "🟡" if utilization > 60 else "🟢"
                
                print(f"{component.replace('_', ' ').title()}:")
                print(f"  {util_icon} Utilization: {utilization:.1f}% ({cap['total_slots'] - cap['available_slots']}/{cap['total_slots']})")
                print(f"  📊 Total: {met.get('total_requests', 0)} | Success: {met.get('success_rate', 0):.1f}%")
                print(f"  ⏱️  Avg Time: {met.get('avg_duration_ms', 0):.0f}ms")
        print()
    
    async def _display_component_performance(self, monitor):
        """Display component performance metrics."""
        print("📈 COMPONENT PERFORMANCE")
        print("-" * 40)
        
        all_stats = monitor.collector.get_all_stats()
        
        for component, stats in all_stats.items():
            if stats['total_requests'] > 0:
                success_icon = "✅" if stats['success_rate'] > 95 else "⚠️" if stats['success_rate'] > 90 else "❌"
                speed_icon = "🚀" if stats['avg_response_time'] < 2000 else "🐌" if stats['avg_response_time'] > 5000 else "⏱️"
                
                print(f"{component}:")
                print(f"  {success_icon} Success Rate: {stats['success_rate']:.1f}% ({stats['successful_requests']}/{stats['total_requests']})")
                print(f"  {speed_icon} Avg Response: {stats['avg_response_time']:.0f}ms (P95: {stats['p95_response_time']:.0f}ms)")
                print(f"  🔄 Current Load: {stats['current_load']} | Peak: {stats['peak_load']}")
                print()
    
    async def _display_alerts(self):
        """Display active alerts and warnings."""
        print("🚨 ALERTS & WARNINGS")
        print("-" * 40)
        
        # Check for common issues
        alerts = []
        
        try:
            # Memory alerts
            memory_mgr = await get_memory_manager()
            memory_stats = memory_mgr.get_memory_stats()
            
            if memory_stats['process_memory_mb'] > 1024:  # > 1GB
                alerts.append("🔴 High memory usage detected")
            
            if memory_stats['temp_files_count'] > 50:
                alerts.append("🟡 Many temporary files present")
            
            # Concurrency alerts
            concurrency_mgr = get_concurrency_manager()
            capacity = await concurrency_mgr.get_capacity_status()
            
            for component, cap in capacity.items():
                if cap['utilization_percent'] > 90:
                    alerts.append(f"🔴 {component} near capacity ({cap['utilization_percent']:.0f}%)")
                elif cap['utilization_percent'] > 75:
                    alerts.append(f"🟡 {component} high utilization ({cap['utilization_percent']:.0f}%)")
            
            # Performance alerts
            monitor = await get_performance_monitor()
            all_stats = monitor.collector.get_all_stats()
            
            for component, stats in all_stats.items():
                if stats['total_requests'] > 0:
                    if stats['success_rate'] < 90:
                        alerts.append(f"🔴 {component} low success rate ({stats['success_rate']:.1f}%)")
                    if stats['avg_response_time'] > 10000:  # > 10s
                        alerts.append(f"🔴 {component} slow response times ({stats['avg_response_time']:.0f}ms)")
            
        except Exception as e:
            alerts.append(f"❌ Error checking alerts: {e}")
        
        if alerts:
            for alert in alerts[:5]:  # Show max 5 alerts
                print(f"  {alert}")
        else:
            print("  ✅ All systems operating normally")
        print()
    
    async def export_current_state(self, filename: str):
        """Export current performance state to file."""
        try:
            monitor = await get_performance_monitor()
            dashboard_data = monitor.get_dashboard_data()
            
            with open(filename, 'w') as f:
                json.dump(dashboard_data, f, indent=2)
            
            print(f"📁 Performance data exported to: {filename}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")


async def main():
    """Main dashboard entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Numbers Bot Performance Dashboard")
    parser.add_argument("--interval", type=float, default=5.0, help="Refresh interval in seconds")
    parser.add_argument("--export", type=str, help="Export current state to file and exit")
    parser.add_argument("--once", action="store_true", help="Show dashboard once and exit")
    
    args = parser.parse_args()
    
    dashboard = PerformanceDashboard(refresh_interval=args.interval)
    
    if args.export:
        await dashboard.export_current_state(args.export)
        return
    
    if args.once:
        await dashboard._display_dashboard()
        return
    
    await dashboard.start()


if __name__ == "__main__":
    asyncio.run(main())