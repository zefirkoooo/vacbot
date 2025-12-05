import json
import logging
from typing import Dict, List, Set
import requests
from config import Config

logger = logging.getLogger(__name__)


class VacancyStorage:
    """Хранилище просмотренных вакансий"""

    def __init__(self, config: Config):
        self.storage_file = config.SEEN_VACANCIES_FILE
        self._seen_ids: Set[str] = self._load()

    def _load(self) -> Set[str]:
        """Загрузка ID просмотренных вакансий"""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Загружено {len(data)} просмотренных вакансий")
                    return set(data)
        except Exception as e:
            logger.error(f"Ошибка загрузки seen_vacancies: {e}")
        return set()

    def save(self):
        """Сохранение ID просмотренных вакансий"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(list(self._seen_ids), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения seen_vacancies: {e}")

    def add(self, vacancy_id: str) -> bool:
        """Добавление ID вакансии"""
        if vacancy_id not in self._seen_ids:
            self._seen_ids.add(vacancy_id)
            return True
        return False

    def contains(self, vacancy_id: str) -> bool:
        """Проверка наличия ID в хранилище"""
        return vacancy_id in self._seen_ids

    def clear(self):
        """Очистка хранилища"""
        self._seen_ids.clear()
        self.save()
        logger.info("Хранилище вакансий очищено")

    def count(self) -> int:
        """Количество просмотренных вакансий"""
        return len(self._seen_ids)


class VacancyFormatter:
    """Форматирование вакансий для отправки"""

    @staticmethod
    def format_vacancy(vacancy: Dict) -> str:
        """Форматирование сообщения о вакансии"""
        name = vacancy.get('name', 'Без названия')
        employer = vacancy.get('employer', {}).get('name', 'Неизвестно')
        area = vacancy.get('area', {}).get('name', 'Не указан')
        url = vacancy.get('alternate_url', '')

        salary_info = VacancyFormatter._format_salary(vacancy.get('salary'))
        experience = VacancyFormatter._format_experience(vacancy.get('experience'))
        employment = VacancyFormatter._format_employment(vacancy.get('employment'))

        message = f"""<b>Новая вакансия!</b>

<b>{name}</b>
Компания: {employer}
Город: {area}
Зарплата: {salary_info}
Опыт: {experience}
Занятость: {employment}

🔗 <a href="{url}">Открыть вакансию</a>
"""
        return message.strip()

    @staticmethod
    def _format_salary(salary: Dict) -> str:
        """Форматирование зарплаты"""
        if not salary:
            return "Не указана"

        from_sal = salary.get('from')
        to_sal = salary.get('to')
        currency = salary.get('currency', 'RUB')

        if from_sal and to_sal:
            return f"{from_sal:,} - {to_sal:,} {currency}"
        elif from_sal:
            return f"От {from_sal:,} {currency}"
        elif to_sal:
            return f"До {to_sal:,} {currency}"

        return "Не указана"

    @staticmethod
    def _format_experience(experience: Dict) -> str:
        """Форматирование опыта"""
        if not experience:
            return "Не указан"
        return experience.get('name', 'Не указан')

    @staticmethod
    def _format_employment(employment: Dict) -> str:
        """Форматирование типа занятости"""
        if not employment:
            return "Не указана"
        return employment.get('name', 'Не указана')


class VacancyParser:
    """Класс для парсинга вакансий с hh.ru"""

    def __init__(self, config: Config):
        self.config = config
        self.storage = VacancyStorage(config)
        self.formatter = VacancyFormatter()

    def fetch_vacancies(self, filters: Dict) -> List[Dict]:
        """Получение вакансий с hh.ru API"""
        try:
            params = self._build_params(filters)

            response = requests.get(
                self.config.HH_API_URL,
                params=params,
                timeout=self.config.HH_API_TIMEOUT,
                headers={'User-Agent': 'VacancyBot/1.0'}
            )
            response.raise_for_status()

            data = response.json()
            vacancies = data.get('items', [])

            logger.info(f"Получено {len(vacancies)} вакансий с hh.ru")
            return vacancies

        except requests.exceptions.Timeout:
            logger.error("Таймаут при запросе к hh.ru API")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к hh.ru API: {e}")
            return []
        except Exception as e:
            logger.error(f"Неожиданная ошибка при парсинге: {e}")
            return []

    def _build_params(self, filters: Dict) -> Dict:
        """Построение параметров запроса"""
        params = {
            'text': filters.get('position', ''),
            'area': filters.get('area_id', 1),
            'per_page': self.config.MAX_VACANCIES_PER_PAGE,
            'page': 0,
        }

        if filters.get('experience'):
            params['experience'] = filters['experience']

        if filters.get('salary'):
            params['salary'] = filters['salary']
            params['only_with_salary'] = True

        return params

    def filter_new_vacancies(self, vacancies: List[Dict]) -> List[Dict]:
        """Фильтрация новых вакансий"""
        new_vacancies = []

        for vacancy in vacancies:
            vacancy_id = str(vacancy.get('id'))

            if vacancy_id and self.storage.add(vacancy_id):
                new_vacancies.append(vacancy)

        if new_vacancies:
            self.storage.save()
            logger.info(f"Найдено {len(new_vacancies)} новых вакансий")
        else:
            logger.info("Новых вакансий не найдено")

        return new_vacancies

    def format_vacancy(self, vacancy: Dict) -> str:
        """Форматирование вакансии"""
        return self.formatter.format_vacancy(vacancy)

    def get_statistics(self) -> Dict:
        """Получение статистики парсера"""
        return {
            'seen_count': self.storage.count()
        }

    def clear_history(self):
        """Очистка истории просмотренных вакансий"""
        self.storage.clear()