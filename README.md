# VacBot
---

## Установка и запуск

### Шаг 1. Клонирование репозитория

```bash
git clone https://github.com/zefirkoooo/vacbot.git
cd vacbot
```

### Шаг 2. Создание виртуального окружения

```bash
python -m venv venv
```

### Шаг 3. Активация виртуального окружения

```bash
venv\Scripts\activate
```

### Шаг 4. Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 5. Настройка переменных окружения

В корне проекта создайте файл `.env` со следующим содержимым:

```ini
TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН
```

#### Как получить TELEGRAM_BOT_TOKEN

1. Откройте Telegram и найдите бота **@BotFather**.
2. Отправьте команду `/newbot`.
3. Следуйте инструкциям: задайте имя и `@username` бота.
4. Скопируйте выданный токен.
5. Вставьте токен в файл `.env` вместо `ВАШ_ТОКЕН`.

### Шаг 6. Запуск бота

```bash
python main.py
```
