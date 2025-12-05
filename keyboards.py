from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class BotKeyboards:
    """Класс для создания клавиатур"""

    def __init__(self, filters_manager):
        self.filters_manager = filters_manager

    def get_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Создание клавиатуры главного меню"""
        buttons = [
            [InlineKeyboardButton(
                text="Установить должность",
                callback_data="set_position"
            )],
            [InlineKeyboardButton(
                text="Установить зарплату",
                callback_data="set_salary"
            )],
            [InlineKeyboardButton(
                text="Установить интервал",
                callback_data="set_interval"
            )],
            [InlineKeyboardButton(
                text="Установить регион",
                callback_data="set_area"
            )],
            [InlineKeyboardButton(
                text="Посмотреть фильтры",
                callback_data="view_filters"
            )],
            [InlineKeyboardButton(
                text="Очистить историю",
                callback_data="clear_history"
            )],
        ]

        if self.filters_manager.get('enabled'):
            buttons.append([InlineKeyboardButton(
                text="Остановить парсер",
                callback_data="stop_parser"
            )])
        else:
            buttons.append([InlineKeyboardButton(
                text="Запустить парсер",
                callback_data="start_parser"
            )])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def get_confirm_keyboard(self) -> InlineKeyboardMarkup:
        """Клавиатура подтверждения"""
        buttons = [
            [
                InlineKeyboardButton(text="Да", callback_data="confirm_yes"),
                InlineKeyboardButton(text="Нет", callback_data="confirm_no")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def get_back_keyboard(self) -> InlineKeyboardMarkup:
        """Клавиатура с кнопкой назад"""
        buttons = [
            [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)