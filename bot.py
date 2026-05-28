import os
import asyncio
from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, MessageCreated, CallbackButton, MessageCallback
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

# 1. Супер-надежная загрузка .env файла
try:
    from dotenv import load_dotenv, find_dotenv
    env_file = find_dotenv()
    if env_file:
        print(f"✅ Найден .env файл по пути: {env_file}")
        load_dotenv(env_file)
    else:
        print("❌ ВНИМАНИЕ: Файл .env не найден! Создайте его в папке с ботом.")
except ImportError:
    pass

# 2. Пытаемся получить токен
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ОШИБКА: Токен не найден в переменных окружения.")
    exit(1) # Останавливаем бота, если токена нет
else:
    print(f"✅ Токен успешно загружен! Начинается: {BOT_TOKEN[:10]}...")

# 3. Настройка и запуск бота
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# 4. Создание клавиатуры
#    InlineKeyboardBuilder позволяет удобно собирать кнопки
reply_kb = InlineKeyboardBuilder()
# Добавляем кнопки в один ряд
reply_kb.row(
    CallbackButton(text='📞 Горячая линия', payload='hotline'),
    CallbackButton(text='🏠 Пункты временного размещения', payload='shelters')
)
# Добавляем второй ряд кнопок
reply_kb.row(
    CallbackButton(text='🤝 Сбор гуманитарной помощи', payload='aid'),
    CallbackButton(text='💰 Выплаты пострадавшим', payload='payments')
)

# 5. Обработчик нажатий на кнопки
@dp.message_callback()
async def message_callback(callback: MessageCallback):
    callback_data = callback.callback.payload
    
    if callback_data == 'hotline':
        answer = "📞 **Телефон горячей линии:** 112 (круглосуточно)\nМЧС: 8 (3952) 399-999"
    elif callback_data == 'shelters':
        answer = "🏠 **ПВР:** Иркутск (школа №5), Тулун (ДК «Прометей») и другие."
    elif callback_data == 'aid':
        answer = "🤝 **Сбор помощи:** Иркутск (ул. Ленина 14), Тулун (ул. Советская 30)"
    elif callback_data == 'payments':
        answer = "💰 **Выплаты:** от 10 000 до 150 000 руб. Оформление в МФЦ."
    else:
        answer = "Пожалуйста, используйте кнопки меню."
    
    await callback.message.answer(answer)
    await callback.message.answer(
        text=f"Могу я ещё чем-нибудь помочь?",
        attachments=[reply_kb.as_markup()]
    )

@dp.message_created()
async def handle_message(event: MessageCreated):
    # Читаем текст сообщения
    user_text = event.message.body.text if event.message.body else "Нет текста"
    print(f"📨 Пришло сообщение: {user_text}")
    chat_id=event.message.recipient.chat_id

    # Отправляем простое подтверждение
    await event.bot.send_message(
        chat_id=chat_id,
        text=f"К сожалению, я не понимаю Ваше сообщение! Пожалуйста, используйте кнопки меню. Вы написали: {user_text[:50]}",
        attachments=[reply_kb.as_markup()]
    )

@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='Добро пожаловать в официальный бот с информацией о паводках!\n\nВыберите нужный пункт:',
        attachments=[reply_kb.as_markup()]
    )    

# 6. Запуск бота
async def main():
    print("🚀 Удаляем старые webhook и запускаем бота...")
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

