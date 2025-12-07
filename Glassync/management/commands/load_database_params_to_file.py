import os
import sys

from django.core.management.base import BaseCommand

from Glassync.task_scheduler.create_cron_job import create_cron_job


class Command(BaseCommand):
    help = 'Load database params to ".env" file.'

    def handle(self, *args, **options):
        env_file = '.env'

        # Перечень переменных окружения, которые хотим записать
        variables = [
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "TELEGRAM_TOKEN"
        ]

        lines = []
        for var in variables:
            value = os.getenv(var)
            if value is None:
                print(f"Внимание: переменная окружения {var} не установлена.")
                value = ""
            lines.append(f"export {var}={value}")

        content = "# Автоматически сгенерированный .env файл\n" + "\n".join(lines) + "\n"

        with open(env_file, 'w') as f:
            f.write(content)

        print(f"{env_file} успешно создан/обновлён.")

        return 0
