from inspect import signature
from http import HTTPStatus

import requests
import telegram


class MockResponseGET:

    def __init__(self, url, params=None, random_sid=None, current_timestamp=None, **kwargs):
        assert (
            url.startswith('https://praktikum.yandex.ru/api/user_api/homework_statuses')
            or
            url.startswith('https://practicum.yandex.ru/api/user_api/homework_statuses')
        ), 'Проверьте, что вы делаете запрос на правильный ресурс API для запроса статуса домашней работы'
        assert 'headers' in kwargs, (
            'Проверьте, что вы передали заголовки `headers` для запроса '
            'статуса домашней работы'
        )
        assert 'Authorization' in kwargs['headers'], (
            'Проверьте, что в параметрах `headers` для запроса статуса '
            'домашней работы добавили Authorization'
        )
        assert kwargs['headers']['Authorization'].startswith('OAuth '), (
            'Проверьте,что в параметрах `headers` для запроса статуса '
            'домашней работы Authorization начинается с OAuth'
        )
        assert params is not None, (
            'Проверьте, что передали параметры `params` для запроса '
            'статуса домашней работы'
        )
        assert 'from_date' in params, (
            'Проверьте, что в параметрах `params` для запроса статуса '
            'домашней работы `from_date`'
        )
        assert params['from_date'] == current_timestamp, (
            'Проверьте, что в параметрах `params` для запроса статуса '
            'домашней работы `from_date` передаете timestamp'
        )
        self.random_sid = random_sid
        self.status_code = HTTPStatus.OK

    def json(self):
        data = {
            "homeworks": [],
            "current_date": self.random_sid
        }
        return data


class MockTelegramBot:

    def __init__(self, token=None, random_sid=None, **kwargs):
        assert token is not None, (
            'Проверьте, что вы передали токен бота Telegram'
        )
        self.random_sid = random_sid

    def send_message(self, chat_id=None, text=None, **kwargs):
        assert chat_id is not None, (
            'Проверьте, что вы передали chat_id= при отправке сообщения ботом Telegram'
        )
        assert text is not None, (
            'Проверьте, что вы передали text= при отправке сообщения ботом Telegram'
        )
        return self.random_sid


class TestHomework:

    def test_logger(self, monkeypatch, random_sid):

        def mock_telegram_bot(*args, **kwargs):
            return MockTelegramBot(*args, random_sid=random_sid, **kwargs)

        monkeypatch.setattr(telegram, "Bot", mock_telegram_bot)

        import bot

        assert hasattr(bot, 'logging'), (
            'Убедитесь, что настроили логирование для вашего бота'
        )

    def test_send_message(self, monkeypatch, random_sid):

        def mock_telegram_bot(*args, **kwargs):
            return MockTelegramBot(*args, random_sid=random_sid, **kwargs)

        monkeypatch.setattr(telegram, "Bot", mock_telegram_bot)

        import bot

        assert hasattr(bot, 'send_message'), (
            'Функция `send_message()` не существует. Не удаляйте её.'
        )
        assert hasattr(bot.send_message, '__call__'), (
            'Функция `send_message()` не существует. Не удаляйте её.'
        )
        assert len(signature(bot.send_message).parameters) == 1, (
            'Функция `send_message()` должна принимать только один аргумент.'
        )

    def test_get_homeworks(self, monkeypatch, random_sid, current_timestamp):

        def mock_response_get(*args, **kwargs):
            return MockResponseGET(*args, random_sid=random_sid, current_timestamp=current_timestamp, **kwargs)

        monkeypatch.setattr(requests, 'get', mock_response_get)

        import bot

        assert hasattr(bot, 'get_homeworks'), (
            'Функция `get_homeworks()` не существует. Не удаляйте её.'
        )
        assert hasattr(bot.get_homeworks, '__call__'), (
            'Функция `get_homeworks()` не существует. Не удаляйте её.'
        )
        assert len(signature(bot.get_homeworks).parameters) == 1, (
            'Функция `get_homeworks()` должна быть с одним параметром.'
        )

        result = bot.get_homeworks(current_timestamp)
        assert type(result) == dict, (
            'Проверьте, что из функции get_homeworks() '
            'возвращается словарь'
        )
        assert 'homeworks' in result, (
            'Проверьте, что из функции get_homeworks() '
            'возвращается словарь содержащий ключ homeworks'
        )
        assert 'current_date' in result, (
            'Проверьте, что из функции get_homeworks() '
            'возвращается словарь содержащий ключ current_date'
        )
        assert result['current_date'] == random_sid, (
            'Проверьте, что из функции get_homeworks() '
            'возращаете ответ API homework_statuses'
        )

    def test_parse_homework_status(self, random_sid):
        test_data = {
            "id": 123,
            "status": "approved",
            "homework_name": str(random_sid),
            "reviewer_comment": "Всё нравится",
            "date_updated": "2020-02-13T14:40:57Z",
            "lesson_name": "Итоговый проект"
        }

        import bot

        assert hasattr(bot, 'parse_homework_status'), (
            'Функция `parse_homework_status()` не существует. Не удаляйте её.'
        )
        assert hasattr(bot.parse_homework_status, '__call__'), (
            'Функция `parse_homework_status()` не существует. Не удаляйте её.'
        )
        assert len(signature(bot.parse_homework_status).parameters) == 1, (
            'Функция `parse_homework_status()` должна быть с одним параметром.'
        )

        result = bot.parse_homework_status(test_data)
        assert result.startswith(f'У вас проверили работу "{random_sid}"'), (
            'Проверьте, что возвращаете название домашней работы в возврате '
            'функции parse_homework_status()'
        )
        assert result.endswith(
            'Ревьюеру всё понравилось, работа зачтена!'
        ), (
            'Проверьте, что возвращаете правильный вердикт для статуса '
            'approved в возврате функции parse_homework_status()'
        )

        test_data['status'] = 'rejected'
        result = bot.parse_homework_status(test_data)
        assert result.startswith(f'У вас проверили работу "{random_sid}"'), (
            'Проверьте, что возвращаете название домашней работы '
            'в возврате функции parse_homework_status()'
        )
        assert result.endswith('К сожалению, в работе нашлись ошибки.'), (
            'Проверьте, что возвращаете правильный вердикт для статуса '
            'rejected в возврате функции parse_homework_status()'
        )
