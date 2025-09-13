from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        # TODO you can import signals here if you plan to use them (e.g., user registration signals)
        # import accounts.signals
        return
