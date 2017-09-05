from django.apps import AppConfig


class Config(AppConfig):
    name = "main_site.apps"
    verbose_name = "Main Site Apps"

    def ready(self):
        import thumbnail
