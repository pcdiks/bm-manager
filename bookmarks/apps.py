from django.apps import AppConfig


class BookmarksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookmarks'
    def ready(self):
        import bookmarks.signals  # Import signals to connect them