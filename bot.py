import os
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from openai import AsyncOpenAI
from aiohttp import web

# --- 1. НАСТРОЙКИ ---
# Берем токен из Environment Variables на Render
TG_TOKEN = os.getenv("BOT_TOKEN") 

# Твой ключ OpenRouter (проверь, чтобы не было лишних пробелов)
OPENROUTER_KEY = "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"

if not TG_TOKEN:
    logging.error("ОШИБКА: Переменная BOT_TOKEN не найдена в настройках Render!")

# --- 2. ИНИЦИАЛИЗАЦИЯ КЛИЕНТОВ ---
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

# Добавляем заголовки, которые требует OpenRouter для работы бесплатных моделей
client = AsyncOpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://render.com", # Обязательно для некоторых моделей
        "X-Title": "DysnilaBot"
    }
)

logging.basicConfig(level=logging.INFO)

# Твой промпт персонажа
SYSTEM_PROMPT = (
    "Ты — 'Главный Душнила Района'. Твоя цель — занудствовать и придираться к словам. "
    "Если кто-то пишет с ошибками — поправь. Отвечай кратко и официально."
)

# --- 3. ВЕБ-СЕРВЕР ДЛЯ RENDER (Чтобы сервис не засыпал) ---
async def handle(request):
    return web.Response(text="Душнила на связи!")

app = web.Application()
app.router.add_get("/", handle)

# --- 4. ЛОГИКА ОБРАБОТКИ СООБЩЕНИЙ ---
@dp.message()
async def neuro_comment(message: types.Message):
    # Игнорируем команды и пустые сообщения
    if not message.text or message.text.startswith('/'):
        return

    # Пока тестируем — убрал шанс ответа, чтобы отвечал ВСЕГДА
    # Если захочешь сделать реже — раскомментируй строку ниже:
    # if random.random() > 0.5: return 

    try:
        # Используем максимально стабильную бесплатную модель
        response = await client.chat.completions.create(
            model="google/gemini-flash-1.5-8b:free", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        
        reply = response.choices[0].message.content
        if reply:
            await message.reply(reply)
        else:
            logging.warning("Нейросеть прислала пустой ответ.")

    except Exception as e:
        logging.error(f"Ошибка нейросети: {e}")

# --- 5. ГЛАВНЫЙ ЗАПУСК ---
async def main():
    # Запускаем бота (skip_updates=True игнорирует сообщения, пришедшие пока бот был выключен)
    asyncio.create_task(dp.start_polling(bot, skip_updates=True))
    
    # Настраиваем веб-сервер
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Порт для Render
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"--- Душнила запущен на порту {port} ---")
    await site.start()
    
    # Удерживаем программу запущенной
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")
