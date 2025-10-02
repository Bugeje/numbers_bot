from numbers_core.core.orchestrator import run, ProfileInput
from numbers_core.intelligence.openrouter_client import OpenRouterClient
from dotenv import load_dotenv
import os

load_dotenv()
# Берём ключ из переменной среды
api_key = os.getenv("OPENROUTER_API_KEY")

# Если ключ не задан, используем мок-клиент
ai_client = OpenRouterClient() if api_key else None

# Пример входных данных
inp = ProfileInput(name="Иван Иванов", birthdate="01.02.1990")

result = run(inp, ai=ai_client)

print("Профиль:")
print(result["profile"])
print("\nАнализ:")
print(result["analysis"]["text"])
