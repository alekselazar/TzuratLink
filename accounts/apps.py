from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from allauth.account.signals import user_signed_up
        from core.backup import backup_async

        def on_user_signed_up(sender, request, user, **kwargs):
            backup_async()

        user_signed_up.connect(on_user_signed_up)
