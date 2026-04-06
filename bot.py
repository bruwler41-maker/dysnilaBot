import os
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from openai import AsyncOpenAI
from aiohttp import web

# --- 1. НАСТРОЙКИ (Берем из переменных окружения) ---
# На Render создай переменную BOT_TOKEN и вставь туда токен из BotFather
TG_TOKEN = os.getenv("BOT_TOKEN") 

# Твой ключ OpenRouter (оставляем так или тоже выносим в Environment как OPENROUTER_KEY)
OPENROUTER_KEY = "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"

if not TG_TOKEN:
    print("ОШИБКА: Переменная BOT_TOKEN не найдена в настройках Render!")

# --- 2. ИНИЦИАЛИЗАЦИЯ ---
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1"
)

logging.basicConfig(level=logging.INFO)

# Промпт для твоего персонажа
SYSTEM_PROMPT = (
    "Ты — 'Главный Душнила Района'. Твоя цель — душнить, занудствовать и придираться к каждому слову. "
    "Если кто-то шутит — объясни, почему это не смешно. Если кто-то пишет с ошибками — поправь его. "
    "Отвечай кратко (1-2 предложения), используй официальный тон."
)

# --- 3. МИНИ-ВЕБ-СЕРВЕР (Для Cron-job и Render) ---
async def handle(request):
    return web.Response(text="Душнила на связи и не спит!")

app = web.Application()
app.router.add_get("/", handle)

# --- 4. ЛОГИКА БОТА ---
@dp.message()
async def neuro_comment(message: types.Message):
    # Не реагируем на команды и пустые сообщения
    if not message.text or message.text.startswith('/'):
        return

    # Шанс ответа 50%, чтобы не спамить слишком сильно (можно убрать эту строку)
    if random.random() > 0.5: return 

    try:
        response = await client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Пользователь {message.from_user.first_name} пишет: {message.text}"}
            ]
        )
        
        reply = response.choices[0].message.content
        await message.reply(reply)

    except Exception as e:
        logging.error(f"Ошибка нейросети: {e}")

# --- 5. ЗАПУСК ---
async def main():
    # Создаем задачу для бота (skip_updates=True пропустит старые сообщения)
    asyncio.create_task(dp.start_polling(bot, skip_updates=True))
    
    # Запускаем веб-сервер на порту Render
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"--- Душнила запущен на порту {port} ---")
    await site.start()
    
    # Бесконечное ожидание
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
