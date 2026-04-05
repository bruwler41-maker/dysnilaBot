import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from openai import AsyncOpenAI
from aiohttp import web

# 1. ДАННЫЕ
TG_TOKEN = "8150129940:AAHUhaMSbSCb05MyyCJyWZ2Cp0uyoYk_NUI"
OPENROUTER_KEY = "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"

# 2. НАСТРОЙКИ
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENROUTER_KEY, base_url="https://openrouter.ai/api/v1")

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = "Ты — Главный Душнила Района. Душни, поправляй ошибки, будь занудой. Отвечай кратко."

# --- МИНИ-ВЕБ-СЕРВЕР ДЛЯ CRON-JOB ---
async def handle(request):
    return web.Response(text="Душнила на связи и не спит!")

app = web.Application()
app.router.add_get("/", handle)

@dp.message()
async def neuro_comment(message: types.Message):
    if not message.text or message.text.startswith('/'):
        return
    try:
        response = await client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        await message.reply(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"Ошибка: {e}")

# --- ЗАПУСК ВСЕГО ВМЕСТЕ ---
async def main():
    # Запускаем бота в фоне
    asyncio.create_task(dp.start_polling(bot))
    
    # Запускаем веб-сервер на порту, который даст Render (обычно 10000)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"--- Душнила запущен на порту {port} ---")
    await site.start()
    
    # Держим скрипт запущенным вечно
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
