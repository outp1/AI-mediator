from aiogram import executor

from bot.views import chatgpt_dispatcher

if __name__ == "__main__":
    executor.start_polling(chatgpt_dispatcher, skip_updates=True)
