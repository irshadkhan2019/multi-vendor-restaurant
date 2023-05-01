from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    # implicitly connect signal handlers
    def ready(self):
        import accounts.signals
