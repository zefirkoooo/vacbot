import asyncio
import logging
from typing import Optional
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties  # ← Добавить импорт

from config import Config
from filters_manager import FiltersManager
from vacancy_parser import VacancyParser
from handlers import BotHandlers
from keyboards import BotKeyboards

logger = logging.getLogger(__name__)

class VacancyBot:
    """Основной класс Telegram-бота"""

    def __init__(self, config: Config):
        self.config = config

        self.bot = Bot(
            token=config.bot_token,
            default=DefaultBotProperties(parse_mode="HTML")
        )

        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)

        self.filters_manager = FiltersManager(config)
        self.parser = VacancyParser(config)
        self.keyboard = BotKeyboards(self.filters_manager)

        self.handlers = BotHandlers(self)
        self.dp.include_router(self.handlers.router)
        self.parser_task: Optional[asyncio.Task] = None

        logger.info("Бот инициализирован")

    async def start_parser(self):
        """Запуск парсера вакансий"""
        self.filters_manager.set('enabled', True)

        if not self.parser_task or self.parser_task.done():
            self.parser_task = asyncio.create_task(self._run_parser())
            logger.info("Парсер запущен")

    async def stop_parser(self):
        """Остановка парсера вакансий"""
        self.filters_manager.set('enabled', False)

        if self.parser_task and not self.parser_task.done():
            self.parser_task.cancel()
            try:
                await self.parser_task
            except asyncio.CancelledError:
                pass
            logger.info("Парсер остановлен")

    async def _run_parser(self):
        """Основной цикл парсера"""
        logger.info("Парсер начал работу")

        while self.filters_manager.get('enabled'):
            try:
                await self._check_and_send_vacancies()
                interval = self.filters_manager.get('interval_minutes', 15)
                interval_seconds = interval * 60
                logger.info(f"Следующая проверка через {interval} минут")
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                logger.info("Парсер остановлен по запросу")
                break
            except Exception as e:
                logger.error(f"Ошибка в парсере: {e}", exc_info=True)
                await asyncio.sleep(60)
        logger.info("Парсер завершил работу")

    async def _check_and_send_vacancies(self):
        """Проверка и отправка новых вакансий"""
        logger.info("Проверка новых вакансий...")
        filters = self.filters_manager.filters
        vacancies = await asyncio.to_thread(
            self.parser.fetch_vacancies,
            filters
        )

        if not vacancies:
            logger.info("Вакансии не получены")
            return
        new_vacancies = self.parser.filter_new_vacancies(vacancies)
        if not new_vacancies:
            logger.info("Новых вакансий нет")
            return
        chat_id = filters.get('chat_id')
        if not chat_id:
            logger.warning("chat_id не установлен, вакансии не отправлены")
            return

        logger.info(f"Отправка {len(new_vacancies)} новых вакансий")

        for vacancy in new_vacancies:
            try:
                message = self.parser.format_vacancy(vacancy)
                await self.bot.send_message(chat_id, message)
                await asyncio.sleep(self.config.MESSAGE_DELAY_SECONDS)

            except Exception as e:
                logger.error(f"Ошибка отправки вакансии: {e}")

        logger.info(f"Отправлено {len(new_vacancies)} вакансий")

    async def start(self):
        """Запуск бота"""
        try:
            logger.info("Запуск бота...")
            if self.filters_manager.get('enabled'):
                await self.start_parser()
            await self.dp.start_polling(self.bot)

        except Exception as e:
            logger.error(f"Критическая ошибка при запуске бота: {e}", exc_info=True)
            raise
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Корректное завершение работы бота"""
        logger.info("Остановка бота...")
        await self.stop_parser()
        await self.bot.session.close()

        logger.info("Бот остановлен")