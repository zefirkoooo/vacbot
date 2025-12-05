import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    """Класс для управления конфигурацией приложения"""

    BASE_DIR = Path(__file__).parent
    FILTERS_FILE = BASE_DIR / "filters.json"
    SEEN_VACANCIES_FILE = BASE_DIR / "seen_vacancies.json"

    HH_API_URL = "https://api.hh.ru/vacancies"
    HH_API_TIMEOUT = 10

    MIN_INTERVAL_MINUTES = 5
    DEFAULT_INTERVAL_MINUTES = 15
    MAX_VACANCIES_PER_PAGE = 50

    MESSAGE_DELAY_SECONDS = 1

    def __init__(self):
        """Инициализация конфигурации"""
        self.bot_token = self._get_bot_token()

    def _get_bot_token(self) -> str:
        """Получение токена бота из переменных окружения или файла"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')

        if token:
            return token

        env_file = self.BASE_DIR / '.env'
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('TELEGRAM_BOT_TOKEN='):
                            return line.split('=', 1)[1].strip()
            except Exception as e:
                logger.error(f"Ошибка чтения .env файла: {e}")

        return "YOUR_BOT_TOKEN_HERE"

    def validate(self) -> bool:
        """Валидация конфигурации"""
        if self.bot_token == "YOUR_BOT_TOKEN_HERE" or not self.bot_token:
            logger.error(
                "Токен бота не установлен!\n"
                "Создайте файл .env и добавьте строку:\n"
                "TELEGRAM_BOT_TOKEN=ваш_токен_здесь\n"
                "Или установите переменную окружения TELEGRAM_BOT_TOKEN"
            )
            return False

        return True

    @staticmethod
    def create_env_template():
        """Создание шаблона .env файла"""
        env_template = """# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Получить токен можно у @BotFather в Telegram
# 1. Напишите @BotFather
# 2. Отправьте /newbot
# 3. Следуйте инструкциям
# 4. Скопируйте токен сюда
"""
        env_file = Path('.env')
        if not env_file.exists():
            try:
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(env_template)
                logger.info("Создан шаблон файла .env")
            except Exception as e:
                logger.error(f"Ошибка создания .env: {e}")


class DefaultFilters:
    """Фильтры по умолчанию"""

    FILTERS = {
        "position": "Python разработчик",
        "area_id": 1,
        "experience": "noExperience",
        "salary": 100000,
        "interval_minutes": 15,
        "chat_id": None,
        "enabled": False
    }

    AREAS = {
        1: "Москва",
        2: "Санкт-Петербург",
        113: "Россия",
        1001: "Другие регионы России"
    }

    EXPERIENCE = {
        "noExperience": "Нет опыта",
        "between1And3": "От 1 до 3 лет",
        "between3And6": "От 3 до 6 лет",
        "moreThan6": "Более 6 лет"
    }