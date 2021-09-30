import logging
import os
import requests
import telegram
import time

from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    filename='program.log',
    level=logging.DEBUG,
    filemode='w')

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler('my_logger.log')
terminal_handler = logging.StreamHandler()

logger.addHandler(file_handler)
logger.addHandler(terminal_handler)

hw_url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
hw_headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    """Returns results of a homework review."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework_status == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    """Returns results of the request to the API."""
    hw_payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        hw_url,
        headers=hw_headers,
        params=hw_payload
    )
    return homework_statuses.json()


def send_message(message):
    """Sends a message containing review results to a bot user."""
    bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )


def main():
    """Executable code."""
    current_timestamp = int(time.time())

    while True:
        try:
            homework_statuses_json = get_homeworks(current_timestamp)
            homeworks_list = homework_statuses_json.get('homeworks')
            if homeworks_list:
                homework = homeworks_list[0]
                message = parse_homework_status(homework)
                send_message(message)
            time.sleep(5 * 60)
            current_timestamp = int(time.time())

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            logger.error(f'Бот упал с ошибкой: {e}', exc_info=True)
            send_message(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
