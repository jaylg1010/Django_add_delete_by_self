from django.apps import AppConfig


class LugConfig(AppConfig):
    name = 'lug'

    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('lg')
