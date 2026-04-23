from .base_settings import *  # noqa

# Put your custom settings here

# `core` is placed first so that `CoreConfig.ready()` runs before any other app's `ready()` - important when `core`
# registers custom lookups or signals that need to be available during the rest of the app initialization.
INSTALLED_APPS = ["core"] + INSTALLED_APPS
