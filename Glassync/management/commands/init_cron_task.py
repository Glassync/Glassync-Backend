import sys

from django.core.management.base import BaseCommand

from Glassync.task_scheduler.create_cron_job import create_cron_job


class Command(BaseCommand):
    help = 'Create a cron job for send notification every minute.'

    def handle(self, *args, **options):
        if not self.__is_linux():
            self.stdout.write('Command should only be run on Linux')
            return -1

        # Вызов команды отправки уведомлений
        command = "python manage.py send_notification"
        # Правило выполнения 1 раз в минуту
        scheduler = '* * * * *'
        # Создать задачу
        success = create_cron_job(command, scheduler)
        if success:
            self.stdout.write('Job created successfully')
            return 0
        else:
            self.stdout.write('Failed to create cron job')
            return -2


    @staticmethod
    def __is_linux():
        return sys.platform.startswith('linux')
