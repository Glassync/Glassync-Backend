import asyncio
from datetime import timedelta, datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from telegram import Bot

from Glassync.models import *


class Command(BaseCommand):
    help = 'Find users to need send notification.'

    def handle(self, *args, **options):
        platforms = NotificationPlatform.objects.all()
        for platform in platforms:
            name = platform.name
            print(name)
            match name:
                case TELEGRAM_PLATFORM_NAME:
                    self.__send_notification_for_telegram_platform(platform)

        return 0

    @classmethod
    def __send_notification_for_telegram_platform(cls, platform: NotificationPlatform):
        # инициализация бота
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

        # для каждой задачи
        tasks = cls.__get_tasks_for_current_minute(platform)
        for task in tasks:
            print(task)
            # Получить параметры уведомлений для пользователя
            notification_settings = UserNotificationSettings.objects.filter(id_user=task.id_user,
                                                                            id_notification_platform=platform).first()

            print(notification_settings)
            # Перейти к следующей задачи, если не удалось или не нужно отправлять пользователю уведомления на эту платформу
            if notification_settings is None or notification_settings.active is False or notification_settings.attr is None:
                continue

            # Составить текст напоминания
            text = cls.__generate_message(task)
            print(text)
            # Получить ID чата
            chat_id = notification_settings.attr

            # Отправить сообщение
            try:
                asyncio.run(bot.send_message(chat_id=chat_id, text=text))
                print(f"Message sent to {task.id_user.first_name} ({chat_id})\n Message text: {text}")
            except Exception as e:
                print(f"Failed to send to {task.id_user.first_name} ({chat_id})\n Message text: {text}\n Error: {e}")

    @staticmethod
    def __get_tasks_for_current_minute(platform: NotificationPlatform):
        # Получаем текущий момент с учётом часового пояса Django
        now = timezone.localtime()

        # Определяем начало минуты — секунды и микросекунды обнуляем
        start_time = now.replace(second=0, microsecond=0)

        # Конец минуты — ровно через 1 минуту
        end_time = start_time + timedelta(minutes=1)

        # Фильтруем задачи по платформе и времени в диапазоне
        tasks = Task.objects.filter(
            platform=platform,
            time__lt=end_time
        )
        return tasks

    @classmethod
    def __generate_message(cls, task: Task):
        # получаем дату события
        event = task.id_event
        date = cls.__get_nearest_date_time_event(event)

        # создание текста сообщения
        text = f'Напоминаю о событии: "{event.name}", которое состоится {date}.'
        return text

    @staticmethod
    def __get_nearest_date_time_event(event:Event):
        # Получаем стартовое значение даты и времени
        event_date = event.date
        event_time = event.time_start
        if event_time is None:
            event_time = '00:00:00'
        event_time = datetime.strptime(str(event_time), '%H:%M:%S').time()
        datetime_value = datetime.combine(event_date, event_time)
        datetime_value = timezone.make_aware(datetime_value, timezone.get_current_timezone())

        # Рассчитать следующую ближайшую дату и время события, если оно повторяющееся
        rule_type = event.recurrence_rule_type
        rule_interval = event.recurrence_rule_interval
        if rule_type is not None and rule_interval is not None:
            # Рассчитать delta значение
            time_delta = None
            match(rule_type) :
                case 'daily':
                    time_delta = timedelta(days=rule_interval)
                case 'weekly':
                    time_delta = timedelta(weeks=rule_interval)
                case 'monthly':
                    time_delta = timedelta(days=rule_interval*30)
                case 'yearly':
                    time_delta = timedelta(days=rule_interval*365)

            # Рассчитать ближайшую дату и время
            if time_delta is not None:
                while datetime_value <= timezone.localtime():
                    datetime_value = datetime_value + time_delta

        # Вернуть дату и время
        return datetime_value
