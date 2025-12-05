import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

class FilterStates(StatesGroup):
    """Состояния для FSM"""
    waiting_for_position = State()
    waiting_for_salary = State()
    waiting_for_interval = State()
    waiting_for_area = State()


class BotHandlers:
    """Класс с обработчиками команд бота"""

    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.router = Router()
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация всех обработчиков"""
        self.router.message(Command("start"))(self.cmd_start)
        self.router.message(Command("menu"))(self.cmd_menu)
        self.router.message(Command("status"))(self.cmd_status)
        self.router.message(Command("help"))(self.cmd_help)
        self.router.message(Command("reset"))(self.cmd_reset)

        self.router.callback_query(F.data == "set_position")(self.set_position_callback)
        self.router.callback_query(F.data == "set_salary")(self.set_salary_callback)
        self.router.callback_query(F.data == "set_interval")(self.set_interval_callback)
        self.router.callback_query(F.data == "set_area")(self.set_area_callback)
        self.router.callback_query(F.data == "start_parser")(self.start_parser_callback)
        self.router.callback_query(F.data == "stop_parser")(self.stop_parser_callback)
        self.router.callback_query(F.data == "view_filters")(self.view_filters_callback)
        self.router.callback_query(F.data == "clear_history")(self.clear_history_callback)

        self.router.message(FilterStates.waiting_for_position)(self.process_position)
        self.router.message(FilterStates.waiting_for_salary)(self.process_salary)
        self.router.message(FilterStates.waiting_for_interval)(self.process_interval)
        self.router.message(FilterStates.waiting_for_area)(self.process_area)

    async def cmd_start(self, message: Message):
        """Обработчик команды /start"""
        self.bot.filters_manager.set('chat_id', message.chat.id)

        await message.answer(
            "<b>Привет! Я бот для мониторинга вакансий на hh.ru</b>\n\n"
            "Я буду автоматически проверять новые вакансии по вашим фильтрам "
            "и присылать их сюда.\n\n"
            "Используйте /menu для настройки фильтров\n"
            "Используйте /status для просмотра статистики\n"
            "Используйте /help для справки",
            reply_markup=self.bot.keyboard.get_menu_keyboard()
        )

    async def cmd_menu(self, message: Message):
        """Обработчик команды /menu"""
        await message.answer(
            "<b>Меню настроек</b>\n\n"
            "Выберите действие:",
            reply_markup=self.bot.keyboard.get_menu_keyboard()
        )

    async def cmd_status(self, message: Message):
        """Обработчик команды /status"""
        filters = self.bot.filters_manager.filters
        stats = self.bot.parser.get_statistics()

        status = "Работает" if filters.get('enabled') else "Остановлен"

        await message.answer(
            f"<b>Статус системы</b>\n\n"
            f"Парсер: {status}\n"
            f"{self.bot.filters_manager.get_summary()}\n"
            f"Просмотрено вакансий: {stats['seen_count']}"
        )

    async def cmd_help(self, message: Message):
        """Обработчик команды /help"""
        
        help_text = """
<b>Справка по командам</b>

<b>Основные команды:</b>
/start - Начать работу с ботом
/menu - Открыть меню настроек
/status - Показать текущий статус
/reset - Сбросить все настройки
/help - Показать эту справку

<b>Как использовать:</b>
1. Настройте фильтры через /menu
2. Запустите парсер кнопкой "️Запустить"
3. Получайте новые вакансии автоматически!

<b>Настройки фильтров:</b>
• Должность - ключевое слово для поиска
• Зарплата - минимальная желаемая зарплата
• Интервал - как часто проверять (мин. 5 мин)
• Регион - где искать вакансии

<b>Подсказки:</b>
Чем точнее фильтры, тем релевантнее вакансии
Не ставьте слишком маленький интервал
Все вакансии сохраняются, дубли не придут
"""
        await message.answer(help_text)

    async def cmd_reset(self, message: Message):
        """Обработчик команды /reset"""
        self.bot.filters_manager.reset()
        await message.answer(
            "<b>Настройки сброшены к значениям по умолчанию</b>\n\n"
            "Используйте /menu для новой настройки.",
            reply_markup=self.bot.keyboard.get_menu_keyboard()
        )

    async def set_position_callback(self, callback: CallbackQuery, state: FSMContext):
        """Начало установки должности"""
        await callback.message.answer(
            "<b>Установка должности</b>\n\n"
            "Введите название должности для поиска:\n"
            "Например: <i>Python разработчик</i>, <i>Frontend developer</i>, <i>Data analyst</i>"
        )
        await state.set_state(FilterStates.waiting_for_position)
        await callback.answer()

    async def set_salary_callback(self, callback: CallbackQuery, state: FSMContext):
        """Начало установки зарплаты"""
        await callback.message.answer(
            "<b>Установка минимальной зарплаты</b>\n\n"
            "Введите минимальную желаемую зарплату (только число):\n"
            "Например: <i>100000</i>, <i>150000</i>, <i>200000</i>"
        )
        await state.set_state(FilterStates.waiting_for_salary)
        await callback.answer()

    async def set_interval_callback(self, callback: CallbackQuery, state: FSMContext):
        """Начало установки интервала"""
        await callback.message.answer(
            "<b>Установка интервала проверки</b>\n\n"
            "Введите интервал проверки в минутах (минимум 5):\n"
            "Например: <i>10</i>, <i>15</i>, <i>30</i>\n\n"
            "Слишком частые проверки могут привести к блокировке API"
        )
        await state.set_state(FilterStates.waiting_for_interval)
        await callback.answer()

    async def set_area_callback(self, callback: CallbackQuery, state: FSMContext):
        """Начало установки региона"""
        await callback.message.answer(
            "<b>Установка региона</b>\n\n"
            "Введите ID региона:\n"
            "• 1 - Москва\n"
            "• 2 - Санкт-Петербург\n"
            "• 113 - Россия (все города)\n"
            "• 1001 - Другие регионы\n\n"
            "Например: <i>1</i> или <i>113</i>"
        )
        await state.set_state(FilterStates.waiting_for_area)
        await callback.answer()

    async def start_parser_callback(self, callback: CallbackQuery):
        """Запуск парсера"""
        if not self.bot.filters_manager.get('position'):
            await callback.answer("Сначала установите должность!", show_alert=True)
            return
        await self.bot.start_parser()
        await callback.message.answer(
            "<b>Парсер запущен!</b>\n\n"
            "Новые вакансии будут приходить автоматически.\n"
            "Используйте /status для проверки состояния.",
            reply_markup=self.bot.keyboard.get_menu_keyboard()
        )
        await callback.answer()

    async def stop_parser_callback(self, callback: CallbackQuery):
        """Остановка парсера"""
        await self.bot.stop_parser()

        await callback.message.answer(
            "<b>Парсер остановлен</b>\n\n"
            "Для повторного запуска нажмите кнопку в меню.",
            reply_markup=self.bot.keyboard.get_menu_keyboard()
        )
        await callback.answer()

    async def view_filters_callback(self, callback: CallbackQuery):
        """Просмотр текущих фильтров"""
        summary = self.bot.filters_manager.get_summary()

        await callback.message.answer(
            f"<b>Текущие фильтры:</b>\n\n{summary}",
            reply_markup=self.bot.keyboard.get_menu_keyboard()
        )
        await callback.answer()

    async def clear_history_callback(self, callback: CallbackQuery):
        """Очистка истории вакансий"""
        self.bot.parser.clear_history()

        await callback.message.answer(
            "<b>История просмотренных вакансий очищена</b>\n\n"
            "Теперь все вакансии будут приходить заново."
        )
        await callback.answer("История очищена!")

    async def process_position(self, message: Message, state: FSMContext):
        """Обработка введенной должности"""
        position = message.text.strip()

        if len(position) < 3:
            await message.answer("Название должности слишком короткое. Попробуйте еще раз:")
            return
        self.bot.filters_manager.set('position', position)
        await message.answer(
            f"<b>Должность установлена:</b> {position}",
            reply_markup=self.bot.keyboard.get_menu_keyboard()
        )
        await state.clear()

    async def process_salary(self, message: Message, state: FSMContext):
        """Обработка введенной зарплаты"""
        try:
            salary = int(message.text.strip())
            if not self.bot.filters_manager.validate_salary(salary):
                await message.answer("Зарплата должна быть больше 0. Попробуйте еще раз:")
                return
            self.bot.filters_manager.set('salary', salary)
            await message.answer(
                f"<b>Минимальная зарплата установлена:</b> {salary:,} руб.",
                reply_markup=self.bot.keyboard.get_menu_keyboard()
            )
            await state.clear()

        except ValueError:
            await message.answer("Пожалуйста, введите корректное число:")

    async def process_interval(self, message: Message, state: FSMContext):
        """Обработка введенного интервала"""
        try:
            interval = int(message.text.strip())
            if not self.bot.filters_manager.validate_interval(interval):
                min_interval = self.bot.config.MIN_INTERVAL_MINUTES
                await message.answer(
                    f"Минимальный интервал - {min_interval} минут. Попробуйте еще раз:"
                )
                return
            self.bot.filters_manager.set('interval_minutes', interval)
            await message.answer(
                f"<b>Интервал установлен:</b> {interval} минут",
                reply_markup=self.bot.keyboard.get_menu_keyboard()
            )
            await state.clear()
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число:")

    async def process_area(self, message: Message, state: FSMContext):
        """Обработка введенного региона"""
        try:
            area_id = int(message.text.strip())
            self.bot.filters_manager.set('area_id', area_id)
            await message.answer(
                f"<b>Регион установлен:</b> ID {area_id}",
                reply_markup=self.bot.keyboard.get_menu_keyboard()
            )
            await state.clear()
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число:")