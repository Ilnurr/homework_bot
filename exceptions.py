class ApiResponseException(Exception):
    """Ошибка при запросе к API."""


pass


class HomeworkError(Exception):
    """Неправильно заполненный словарь homework."""


pass


class TelegramError(Exception):
    """Ошибки Telegram."""


pass
