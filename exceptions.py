class ApiResponseException(Exception):
    """Ошибка при запросе к API."""

    def __str__(self):
        """Ошибка в запросе к API."""
        return "Ошибка при запросе к API."


class HomeworkError(Exception):
    """Неправильно заполненный словарь homework."""

    def __str__(self):
        """Ошибка в заполнении словаря."""
        return "Неправильно заполненный словарь homework."
