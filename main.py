import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import load_config
from database import Database
from services.ai import AIService
from services.file_builder import FileBuilder
from handlers.commands import router as commands_router
from handlers.generate import router as generate_router, register_generate_handlers


async def main():
    logging.basicConfig(level=logging.INFO)
    config = load_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    db = Database(config.db_path)
    await db.init()

    ai = AIService(api_key=config.openai_api_key, model=config.openai_model)
    file_builder = FileBuilder(config.generated_dir)

    # Зависимости пробрасываются во все хендлеры через workflow_data (DI aiogram 3)
    dp["db"] = db
    dp["ai"] = ai
    dp["file_builder"] = file_builder

    # Команды (/start, /help, /clear, /code) должны идти раньше общего обработчика текста
    dp.include_router(commands_router)
    register_generate_handlers(generate_router)
    dp.include_router(generate_router)

    logging.info("CodeBot запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
