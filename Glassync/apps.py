from django.apps import AppConfig
from django.core.management import call_command


class GlassyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Glassync'

    def ready(self):
        call_command('init_cron_task')
