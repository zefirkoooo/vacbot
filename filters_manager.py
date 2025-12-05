import json
import logging
from pathlib import Path
from typing import Dict
from config import Config, DefaultFilters

logger = logging.getLogger(__name__)


class FiltersManager:
    """Менеджер для работы с фильтрами"""

    def __init__(self, config: Config):
        self.config = config
        self.filters_file = config.FILTERS_FILE
        self._filters = None

    @property
    def filters(self) -> Dict:
        """Получение текущих фильтров (ленивая загрузка)"""
        if self._filters is None:
            self._filters = self.load()
        return self._filters

    def load(self) -> Dict:
        """Загрузка фильтров из JSON"""
        try:
            if self.filters_file.exists():
                with open(self.filters_file, 'r', encoding='utf-8') as f:
                    loaded_filters = json.load(f)
                    logger.info("Фильтры загружены из файла")
                    return loaded_filters
            else:
                logger.info("Файл фильтров не найден, создаем новый")
                return self.create_default()
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return self.create_default()
        except Exception as e:
            logger.error(f"Ошибка загрузки filters.json: {e}")
            return self.create_default()

    def create_default(self) -> Dict:
        """Создание фильтров по умолчанию"""
        default_filters = DefaultFilters.FILTERS.copy()
        self.save(default_filters)
        logger.info("Созданы фильтры по умолчанию")
        return default_filters

    def save(self, filters: Dict = None):
        """Сохранение фильтров в JSON"""
        if filters is None:
            filters = self._filters

        try:
            with open(self.filters_file, 'w', encoding='utf-8') as f:
                json.dump(filters, f, ensure_ascii=False, indent=2)
            self._filters = filters
            logger.info("Фильтры успешно сохранены")
        except Exception as e:
            logger.error(f"Ошибка сохранения filters.json: {e}")

    def update(self, **kwargs):
        """Обновление отдельных полей фильтров"""
        current_filters = self.filters
        current_filters.update(kwargs)
        self.save(current_filters)

    def get(self, key: str, default=None):
        """Получение значения фильтра"""
        return self.filters.get(key, default)

    def set(self, key: str, value):
        """Установка значения фильтра"""
        self.update(**{key: value})

    def reset(self):
        """Сброс к настройкам по умолчанию"""
        self._filters = self.create_default()
        logger.info("Фильтры сброшены к значениям по умолчанию")

    def get_summary(self) -> str:
        """Получение текстового описания фильтров"""
        f = self.filters

        area_name = DefaultFilters.AREAS.get(f.get('area_id', 1), "Неизвестно")
        experience_name = DefaultFilters.EXPERIENCE.get(
            f.get('experience', 'noExperience'),
            "Не указан"
        )

        summary = (
            f"Должность: {f.get('position', 'Не задана')}\n"
            f"Регион: {area_name}\n"
            f"Опыт: {experience_name}\n"
            f"Зарплата от: {f.get('salary', 'Не задана')}\n"
            f"Интервал: {f.get('interval_minutes', 15)} мин\n"
            f"Статус: {'Работает' if f.get('enabled') else 'Остановлен'}"
        )

        return summary

    def validate_interval(self, interval: int) -> bool:
        """Проверка валидности интервала"""
        return interval >= self.config.MIN_INTERVAL_MINUTES

    def validate_salary(self, salary: int) -> bool:
        """Проверка валидности зарплаты"""
        return salary > 0