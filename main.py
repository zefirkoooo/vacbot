import asyncio
import logging
from config import Config
from bot import VacancyBot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    config = Config()
    if not config.validate():
        logger.error("Ошибка конфигурации. Проверьте настройки!")
        return

    bot = VacancyBot(config)
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
