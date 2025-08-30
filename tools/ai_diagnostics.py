#!/usr/bin/env python3
"""
AI Diagnostics Tool for Numbers Bot
Helps diagnose and troubleshoot AI analysis errors.
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from intelligence.engine import ask_openrouter
from intelligence.analysis import get_ai_analysis
from intelligence.prompts import profile_prompt
from intelligence.system_prompts import SYSTEM_PROMPTS
from calc.profile import calculate_core_profile
from helpers.http_pool import get_http_pool
from helpers.concurrency import get_concurrency_manager


class AIDiagnostics:
    """AI system diagnostics and troubleshooting."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "unknown"
        }
    
    async def run_full_diagnostics(self) -> dict:
        """Run complete AI diagnostics."""
        print("🔍 Запуск полной диагностики AI системы...")
        print("=" * 60)
        
        # Configuration check
        await self._test_configuration()
        
        # HTTP client pool check
        await self._test_http_pool()
        
        # Concurrency manager check
        await self._test_concurrency()
        
        # OpenRouter API connectivity
        await self._test_api_connectivity()
        
        # End-to-end analysis test
        await self._test_end_to_end_analysis()
        
        # Performance test
        await self._test_performance()
        
        # Summary
        self._generate_summary()
        
        return self.results
    
    async def _test_configuration(self):
        """Test configuration settings."""
        print("📋 Проверка конфигурации...")
        
        test_result = {
            "status": "success",
            "details": {},
            "errors": []
        }
        
        # Check API key
        if not settings.ai.openrouter_api_key:
            test_result["status"] = "error"
            test_result["errors"].append("Отсутствует OPENROUTER_API_KEY")
        else:
            key_preview = settings.ai.openrouter_api_key[:10] + "..."
            test_result["details"]["api_key"] = f"Установлен ({key_preview})"
        
        # Check other settings
        test_result["details"]["base_url"] = settings.ai.openrouter_base_url
        test_result["details"]["model"] = settings.ai.model
        test_result["details"]["temperature"] = settings.ai.temperature
        test_result["details"]["max_tokens"] = settings.ai.max_tokens
        test_result["details"]["timeout"] = settings.ai.timeout
        
        # Check concurrency settings
        test_result["details"]["ai_semaphore_limit"] = settings.ai_semaphore_limit
        test_result["details"]["http_timeout"] = settings.http_timeout
        
        self.results["tests"]["configuration"] = test_result
        
        if test_result["status"] == "success":
            print("   ✅ Конфигурация корректна")
        else:
            print(f"   ❌ Проблемы с конфигурацией: {', '.join(test_result['errors'])}")
    
    async def _test_http_pool(self):
        """Test HTTP client pool."""
        print("🌐 Проверка HTTP пула...")
        
        test_result = {
            "status": "success",
            "details": {},
            "errors": []
        }
        
        try:
            http_pool = await get_http_pool()
            health = await http_pool.health_check()
            
            test_result["details"]["pool_status"] = health["status"]
            test_result["details"]["healthy_clients"] = health["healthy_clients"]
            test_result["details"]["total_clients"] = health["total_clients"]
            test_result["details"]["health_percentage"] = health["health_percentage"]
            
            if health["health_percentage"] < 100:
                test_result["status"] = "warning"
                test_result["errors"].append(f"Не все HTTP клиенты здоровы ({health['health_percentage']:.1f}%)")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(f"Ошибка HTTP пула: {e}")
        
        self.results["tests"]["http_pool"] = test_result
        
        if test_result["status"] == "success":
            print("   ✅ HTTP пул работает корректно")
        elif test_result["status"] == "warning":
            print(f"   ⚠️ HTTP пул: {', '.join(test_result['errors'])}")
        else:
            print(f"   ❌ HTTP пул: {', '.join(test_result['errors'])}")
    
    async def _test_concurrency(self):
        """Test concurrency manager."""
        print("⚡ Проверка управления конкурентностью...")
        
        test_result = {
            "status": "success",
            "details": {},
            "errors": []
        }
        
        try:
            concurrency_mgr = get_concurrency_manager()
            
            # Check capacity
            capacity = await concurrency_mgr.get_capacity_status()
            test_result["details"]["ai_capacity"] = capacity.get("ai_requests", {})
            test_result["details"]["pdf_capacity"] = capacity.get("pdf_generation", {})
            
            # Check metrics
            metrics = await concurrency_mgr.get_metrics()
            test_result["details"]["ai_metrics"] = metrics.get("ai_requests", {})
            
            # Health check
            health = await concurrency_mgr.health_check()
            test_result["details"]["health"] = health
            
            if not health.get("overall_healthy", False):
                test_result["status"] = "warning"
                test_result["errors"].append("Проблемы со здоровьем системы конкурентности")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(f"Ошибка управления конкурентностью: {e}")
        
        self.results["tests"]["concurrency"] = test_result
        
        if test_result["status"] == "success":
            print("   ✅ Управление конкурентностью работает")
        elif test_result["status"] == "warning":
            print(f"   ⚠️ Конкурентность: {', '.join(test_result['errors'])}")
        else:
            print(f"   ❌ Конкурентность: {', '.join(test_result['errors'])}")
    
    async def _test_api_connectivity(self):
        """Test OpenRouter API connectivity."""
        print("🤖 Проверка подключения к OpenRouter API...")
        
        test_result = {
            "status": "success",
            "details": {},
            "errors": []
        }
        
        try:
            # Simple test request
            system_prompt = "You are a helpful assistant."
            user_prompt = "Say 'Hello, this is a test!' in Russian."
            
            start_time = asyncio.get_event_loop().time()
            response = await ask_openrouter(system_prompt, user_prompt, max_tokens=50)
            end_time = asyncio.get_event_loop().time()
            
            response_time = end_time - start_time
            test_result["details"]["response_time"] = f"{response_time:.2f}s"
            test_result["details"]["response_length"] = len(response)
            test_result["details"]["response_preview"] = response[:100] + "..." if len(response) > 100 else response
            
            # Check if response indicates an error
            if response.startswith("❌"):
                test_result["status"] = "error"
                test_result["errors"].append(f"API вернул ошибку: {response}")
            elif len(response) < 5:
                test_result["status"] = "warning"
                test_result["errors"].append("API вернул очень короткий ответ")
            elif response_time > 30:
                test_result["status"] = "warning"
                test_result["errors"].append(f"Медленный ответ API ({response_time:.1f}s)")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(f"Ошибка API: {e}")
        
        self.results["tests"]["api_connectivity"] = test_result
        
        if test_result["status"] == "success":
            print(f"   ✅ API отвечает корректно ({test_result['details']['response_time']})")
        elif test_result["status"] == "warning":
            print(f"   ⚠️ API: {', '.join(test_result['errors'])}")
        else:
            print(f"   ❌ API: {', '.join(test_result['errors'])}")
    
    async def _test_end_to_end_analysis(self):
        """Test complete analysis pipeline."""
        print("🧠 Проверка полного цикла анализа...")
        
        test_result = {
            "status": "success",
            "details": {},
            "errors": []
        }
        
        try:
            # Create test profile
            test_name = "Иван Иванов"
            test_birthdate = "15.03.1990"
            
            # Calculate profile
            profile = calculate_core_profile(test_name, test_birthdate)
            test_result["details"]["profile_keys"] = list(profile.keys())
            
            # Test AI analysis
            start_time = asyncio.get_event_loop().time()
            analysis = await get_ai_analysis(profile)
            end_time = asyncio.get_event_loop().time()
            
            analysis_time = end_time - start_time
            test_result["details"]["analysis_time"] = f"{analysis_time:.2f}s"
            test_result["details"]["analysis_length"] = len(analysis)
            test_result["details"]["analysis_preview"] = analysis[:200] + "..." if len(analysis) > 200 else analysis
            
            # Check analysis quality
            if analysis.startswith("❌") or analysis.startswith("⚠️"):
                test_result["status"] = "error"
                test_result["errors"].append(f"Анализ содержит ошибку: {analysis[:100]}")
            elif len(analysis) < 50:
                test_result["status"] = "warning"
                test_result["errors"].append("Анализ слишком короткий")
            elif analysis_time > 45:
                test_result["status"] = "warning"
                test_result["errors"].append(f"Медленный анализ ({analysis_time:.1f}s)")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(f"Ошибка полного цикла: {e}")
        
        self.results["tests"]["end_to_end"] = test_result
        
        if test_result["status"] == "success":
            print(f"   ✅ Полный цикл работает ({test_result['details']['analysis_time']})")
        elif test_result["status"] == "warning":
            print(f"   ⚠️ Полный цикл: {', '.join(test_result['errors'])}")
        else:
            print(f"   ❌ Полный цикл: {', '.join(test_result['errors'])}")
    
    async def _test_performance(self):
        """Test performance under load."""
        print("🚀 Тест производительности (5 параллельных запросов)...")
        
        test_result = {
            "status": "success",
            "details": {},
            "errors": []
        }
        
        try:
            # Create test profile
            test_name = "Тест Производительности"
            test_birthdate = "01.01.1985"
            profile = calculate_core_profile(test_name, test_birthdate)
            
            # Run 5 concurrent requests
            start_time = asyncio.get_event_loop().time()
            
            tasks = []
            for i in range(5):
                task = asyncio.create_task(get_ai_analysis(profile))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = asyncio.get_event_loop().time()
            
            total_time = end_time - start_time
            test_result["details"]["total_time"] = f"{total_time:.2f}s"
            test_result["details"]["concurrent_requests"] = len(tasks)
            
            # Analyze results
            successful = 0
            failed = 0
            errors = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed += 1
                    errors.append(f"Запрос {i+1}: {result}")
                elif isinstance(result, str) and (result.startswith("❌") or result.startswith("⚠️")):
                    failed += 1
                    errors.append(f"Запрос {i+1}: {result[:50]}")
                else:
                    successful += 1
            
            test_result["details"]["successful"] = successful
            test_result["details"]["failed"] = failed
            test_result["details"]["success_rate"] = f"{successful/len(tasks)*100:.1f}%"
            
            if failed > 0:
                test_result["status"] = "warning" if successful > failed else "error"
                test_result["errors"] = errors[:3]  # Show first 3 errors
            
            if total_time > 60:  # More than 1 minute for 5 requests
                test_result["status"] = "warning"
                test_result["errors"].append(f"Медленная производительность ({total_time:.1f}s)")
        
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(f"Ошибка теста производительности: {e}")
        
        self.results["tests"]["performance"] = test_result
        
        if test_result["status"] == "success":
            print(f"   ✅ Производительность: {test_result['details']['success_rate']} успешно ({test_result['details']['total_time']})")
        elif test_result["status"] == "warning":
            print(f"   ⚠️ Производительность: {', '.join(test_result['errors'][:2])}")
        else:
            print(f"   ❌ Производительность: {', '.join(test_result['errors'][:2])}")
    
    def _generate_summary(self):
        """Generate overall diagnostics summary."""
        print("\n" + "=" * 60)
        print("📊 СВОДКА ДИАГНОСТИКИ")
        print("=" * 60)
        
        error_count = 0
        warning_count = 0
        success_count = 0
        
        for test_name, test_result in self.results["tests"].items():
            status = test_result["status"]
            if status == "error":
                error_count += 1
            elif status == "warning":
                warning_count += 1
            else:
                success_count += 1
        
        total_tests = len(self.results["tests"])
        
        print(f"Всего тестов: {total_tests}")
        print(f"✅ Успешно: {success_count}")
        print(f"⚠️ Предупреждения: {warning_count}")
        print(f"❌ Ошибки: {error_count}")
        
        # Overall status
        if error_count > 0:
            self.results["overall_status"] = "error"
            print("\n🔴 ОБЩИЙ СТАТУС: КРИТИЧЕСКИЕ ПРОБЛЕМЫ")
            print("Необходимо исправить ошибки перед использованием AI анализа.")
        elif warning_count > 0:
            self.results["overall_status"] = "warning"
            print("\n🟡 ОБЩИЙ СТАТУС: ЧАСТИЧНЫЕ ПРОБЛЕМЫ")
            print("AI анализ может работать, но рекомендуется исправить предупреждения.")
        else:
            self.results["overall_status"] = "success"
            print("\n🟢 ОБЩИЙ СТАТУС: ВСЕ СИСТЕМЫ РАБОТАЮТ")
            print("AI анализ готов к работе!")
        
        # Recommendations
        print("\n💡 РЕКОМЕНДАЦИИ:")
        
        if error_count > 0:
            print("1. Проверьте конфигурацию .env файла")
            print("2. Убедитесь, что OPENROUTER_API_KEY установлен корректно")
            print("3. Проверьте интернет соединение")
            print("4. Убедитесь, что на счету OpenRouter достаточно средств")
        
        if warning_count > 0:
            print("1. Рассмотрите увеличение таймаутов в конфигурации")
            print("2. Проверьте стабильность интернет соединения")
            print("3. Мониторьте использование ресурсов сервера")
        
        if error_count == 0 and warning_count == 0:
            print("1. Система работает оптимально")
            print("2. Рекомендуется периодически запускать диагностику")
            print("3. Мониторьте производительность при высокой нагрузке")
    
    def save_report(self, filename: str):
        """Save diagnostics report to file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n📁 Отчет сохранен: {filename}")


async def main():
    """Main diagnostics runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI System Diagnostics")
    parser.add_argument("--output", type=str, help="Save detailed report to file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run diagnostics
    diagnostics = AIDiagnostics()
    
    try:
        results = await diagnostics.run_full_diagnostics()
        
        # Save report if requested
        if args.output:
            diagnostics.save_report(args.output)
        
        # Exit with appropriate code
        if results["overall_status"] == "error":
            sys.exit(1)
        elif results["overall_status"] == "warning":
            sys.exit(2)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n🛑 Диагностика прервана пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Ошибка диагностики: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())