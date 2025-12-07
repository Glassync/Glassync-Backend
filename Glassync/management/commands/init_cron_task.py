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
        command = '/bin/bash -c "source /app/.env && /usr/bin/python3 /app/manage.py send_notifications >> /var/log/my_cron.log 2>&1"'
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
