import os
import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from openai import AsyncOpenAI
from aiohttp import web

# --- 1. НАСТРОЙКИ ---
# Токен бота берется из настроек Render (Environment Variables)
TG_TOKEN = os.getenv("BOT_TOKEN") 

# Твой новый ключ OpenRouter, который ты мне скинул
OPENROUTER_KEY = "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"

# --- 2. ИНИЦИАЛИЗАЦИЯ ---
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

# Настраиваем клиент OpenRouter с нужными заголовками
client = AsyncOpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://render.com",
        "X-Title": "DysnilaBot"
    }
)

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = (
    "Ты — 'Главный Душнила Района'. Твоя цель — занудствовать и придираться к словам. "
    "Если кто-то пишет с ошибками — поправь. Отвечай кратко, официально и очень душно."
)

# --- 3. ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Душнила активен и занудствует!")

app = web.Application()
app.router.add_get("/", handle)

# --- 4. ЛОГИКА БОТА ---
@dp.message()
async def neuro_comment(message: types.Message):
    if not message.text or message.text.startswith('/'):
        return

    # Убрал шанс ответа, чтобы он отвечал ВСЕГДА (для теста)
    try:
        # Используем мощную и стабильную бесплатную модель Llama 3.1
        response = await client.chat.completions.create(
           model="mistralai/mistral-7b-instruct:free", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        
        reply = response.choices[0].message.content
        if reply:
            await message.reply(reply)

    except Exception as e:
        logging.error(f"Ошибка: {e}")

# --- 5. ЗАПУСК ---
async def main():
    # Игнорируем старые сообщения при запуске
    asyncio.create_task(dp.start_polling(bot, skip_updates=True))
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"--- Бот запущен на порту {port} ---")
    await site.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
