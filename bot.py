import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from openai import AsyncOpenAI

# 1. ТВОИ ДАННЫЕ (НЕ ЗАБУДЬ ВСТАВИТЬ TG_TOKEN)
TG_TOKEN = "8150129940:AAFure-gODdMyOkrI04v6OiycEI8o7aBLhw"
OPENROUTER_KEY = "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"

# 2. НАСТРОЙКА КЛИЕНТОВ
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Включаем логирование, чтобы видеть ошибки в консоли
logging.basicConfig(level=logging.INFO)

# 3. ПРОМПТ ДЛЯ ГЛАВНОГО ДУШНИЛЫ РАЙОНА
SYSTEM_PROMPT = (
    "Ты — бот в чате друзей по имени 'Главный Душнила Района'. "
    "Твоя задача: душнить, занудствовать и придираться к каждому слову. "
    "Если кто-то шутит — объясни, почему это не смешно. "
    "Если кто-то пишет с ошибками — поправь его максимально высокомерно. "
    "Используй заумные слова и канцеляризмы. Отвечай кратко, 1-2 предложения."
)

@dp.message()
async def neuro_comment(message: types.Message):
    # Не реагируем на команды (например, /start) и на сообщения без текста
    if not message.text or message.text.startswith('/'):
        return

    try:
        # Запрос к нейросети через OpenRouter
        response = await client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Пользователь {message.from_user.first_name} пишет: {message.text}"}
            ]
        )
        
        reply = response.choices[0].message.content
        
        # Отвечаем на сообщение друга
        await message.reply(reply)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

async def main():
    print("--- Душнила вышел на дежурство! ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Душнила ушел проветриваться...")
