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
                meta_cache_key = f'page_meta:{instance.ref}'
                cache.delete(cache_key)
                cache.delete(meta_cache_key)
            except Exception:
                # Don't fail if cache is unavailable
                pass
        
        from .models import Page
        post_save.connect(invalidate_cache, sender=Page)
        post_delete.connect(invalidate_cache, sender=Page)
        
        # Pre-render Daf Yomi on startup (optional, set PRERENDER_ON_STARTUP=True in settings)
        from django.conf import settings
        if getattr(settings, 'PRERENDER_ON_STARTUP', False):
            try:
                from .utils import prerender_daf_yomi
                import threading
                
                # Run in background thread to avoid blocking startup
                def warm_cache():
                    try:
                        prerender_daf_yomi(cache_duration=86400)
                        print("[TzuratLink] Daf Yomi pages pre-rendered successfully")
                    except Exception as e:
                        print(f"[TzuratLink] Warning: Failed to pre-render Daf Yomi: {e}")
                
                thread = threading.Thread(target=warm_cache, daemon=True)
                thread.start()
            except Exception:
                pass