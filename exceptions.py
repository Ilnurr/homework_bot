class ApiResponseException(Exception):
    """Ошибка при запросе к API."""


class HomeworkError(Exception):
    """Неправильно заполненный словарь homework."""


class TelegramError(Exception):
    """Ошибки Telegram."""
