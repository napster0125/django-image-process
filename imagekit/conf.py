from appconf import AppConf
from django.conf import settings


class ImageKitConf(AppConf):
    CACHEFILE_NAMER = 'imagekit.cachefiles.namers.hash'
    SPEC_CACHEFILE_NAMER = 'imagekit.cachefiles.namers.source_name_as_path'
    CACHEFILE_DIR = 'CACHE/images'
    DEFAULT_CACHEFILE_BACKEND = 'imagekit.cachefiles.backends.Simple'
    DEFAULT_CACHEFILE_STRATEGY = 'imagekit.cachefiles.strategies.JustInTime'

    DEFAULT_FILE_STORAGE = None

    CACHE_BACKEND = None
    CACHE_PREFIX = 'imagekit:'
    USE_MEMCACHED_SAFE_CACHE_KEY = True

    def configure_cache_backend(self, value):
        if value is None:
            # DEFAULT_CACHE_ALIAS doesn't exist in Django<=1.2
            try:
                from django.core.cache import DEFAULT_CACHE_ALIAS
                default_cache_alias = DEFAULT_CACHE_ALIAS or 'default'
            except ImportError:
                default_cache_alias = 'default'

            if default_cache_alias in getattr(settings, 'CACHES', {}):
                value = default_cache_alias
            else:
                raise ValueError("The default cache alias '%s' is not available in CACHES" % value)

        return value

    def configure_default_file_storage(self, value):
        if value is None:
            value = settings.DEFAULT_FILE_STORAGE
        return value
