from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    verbose_name = 'Inventory Management'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        
        This ensures signals are connected on app initialization.
        """
        import inventory.signals  # noqa: F401
