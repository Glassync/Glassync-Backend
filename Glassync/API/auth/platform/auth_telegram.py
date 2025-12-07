import asyncio
import hashlib
import hmac
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from telegram import Bot

from Glassync.models import UserNotificationSettings, NotificationPlatform
from backend.settings import TELEGRAM_PLATFORM_NAME, TELEGRAM_BOT_TOKEN


def send_greeting_message(chat_id: int):
    """
    Отправляет приветственное сообщение пользователю.
    :param chat_id: ID чата с пользователем.
    """
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    asyncio.run(bot.send_message(chat_id=chat_id, text="Вы успешно подключили отправку напоминаний в телеграм! "))

def data_hash_check(data):
    """
    Проверяет корректность данных авторизации по хэшу.
    """
    # Получить хэш
    received_hash = data.get('hash')

    # Вернуть неудачу, если хэш не найден
    if not received_hash:
        return False

    # Создать словарь без поля hash
    data_check = {k: v for k, v in data.items() if k != 'hash'}

    # Сформировать строку key=value через \n, отсортированную по ключу
    data_check_string = '\n'.join(
        f"{k}={v}" for k, v in sorted(data_check.items())
    )

    # Ключ для HMAC — SHA256 от bot_token
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()

    # Вычислить HMAC-SHA256
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # Вернуть результат проверки, сравнив полученный HMAC с пришедшим hash (в нижнем регистре)
    return hmac_hash == received_hash.lower()

@csrf_exempt
@login_required
@require_POST
def handle_telegram_auth_result(request):
    """
    Обработчик результата авторизации пользователя через телеграмм.
    """
    # Получение информации из запроса
    data = json.loads(request.body)

    # Вернуть ошибку, если не пройдена проверка корректности данных с хэшом
    data_hash_check(data)
    if not data_hash_check(data):
        return HttpResponse(status=400)

    # Получение настроек уведомлений с данными о платформе в одном запросе
    notifications_settings = UserNotificationSettings.objects.filter(
        id_user=request.user.id
    ).select_related('id_notification_platform').filter(
        id_notification_platform__name=TELEGRAM_PLATFORM_NAME
    ).first()

    # Получаем id чата с пользователем
    user_telegram_id = data.get('id')

    # Отправляем приветственное сообщение, если это необходимо
    if (notifications_settings.attr != user_telegram_id):
        send_greeting_message(user_telegram_id)

    # Обновляем запись в базе данных
    notifications_settings.attr = user_telegram_id
    notifications_settings.active = True
    notifications_settings.save()

    # Возвращаем корректный статус
    return HttpResponse(status=200)
