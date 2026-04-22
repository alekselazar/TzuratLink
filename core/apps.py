from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from . import mongo
        from django.core.cache import cache
        from django.db.models.signals import post_save, post_delete

        mongo.init_mongo()
        
        # Set up cache invalidation signals
        def invalidate_cache(sender, instance, **kwargs):
            """Invalidate cache when Page is saved or deleted"""
            try:
                cache_key = f'page_data:{instance.ref}'
                cache.delete(cache_key)
            except Exception:
                # Don't fail if cache is unavailable
                pass
        
        from .models import Page
        post_save.connect(invalidate_cache, sender=Page)
        post_delete.connect(invalidate_cache, sender=Page)