from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Find users to need send notification.'

    def handle(self, *args, **options):
        # ToDo: Здесь должен быть код реализации отправки уведомлений пользователям.
        return 0
