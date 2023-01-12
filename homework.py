import logging
import sys
import os
import time
import requests
import telegram
from telegram import Bot, TelegramError
from dotenv import load_dotenv
from exceptions import ApiResponseException, HomeworkError


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s : [%(levelname)s] : %(name)s : %(message)s")
)
logger.addHandler(file_handler)


def check_tokens():
    """Проверка переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot: Bot, message):
    """Отправляем сообщение в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug("Бот отправляет сообщение")
    except TelegramError:
        logger.error("Не удалось отправить сообщение")


def get_api_answer(timestamp):
    """Запрос к единственному эндпоинту API Yandex.Practicum."""
    try:
        api_answer = requests.get(
            ENDPOINT, headers=HEADERS, params={"from_date": timestamp}
        )
    except Exception as error:
        raise Exception(f'Эндпоинт не доступен {api_answer}: {error}')
    if api_answer.status_code != requests.codes.ok:
        logging.error(f'Ошибка {api_answer.status_code}')
        raise ApiResponseException(
            f'Ошибка при запросе к API {api_answer.status_code}')
    try:
        return api_answer.json()
    except ValueError:
        raise ValueError("Не удалось получить данные")


def check_response(response):
    """Проверка ответа API."""
    if not isinstance(response, dict) or response is None:
        raise TypeError('Ответ  не словарь dict')
    logger.info("Получаем homeworks")
    homeworks = response.get("homeworks")
    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError('Пустой ответ "response" от API')
    if not isinstance(homeworks, list):
        raise TypeError("Переменная 'homeworks' не является списком")
    return homeworks


def parse_status(homework):
    """Статус о домашней работе."""
    homework_name = homework.get("homework_name", None)
    homework_status = homework.get("status", None)
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if homework_name is None or homework_status not in HOMEWORK_VERDICTS:
        raise HomeworkError(f'Незвестны статус:{homework_status}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical(
            'Проверьте количество переменных окружения'
        )
        sys.exit('Отсутствует обязательная переменная окружения')
    status = ''
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            logger.debug("Пуск бота")
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                homework_status = parse_status(homeworks[0])
            else:
                homework_status = 'Новых задач нет '
            if homework_status != status:
                send_message(bot, homework_status)
            logger.debug("New статус не обнаружен")
            timestamp = response.get('current_date', timestamp)
            logger.debug("Сон")
        except TelegramError as error:
            message = f"Ошибка в программы: {error}"
            logger.error(message, exc_info=True)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    main()
