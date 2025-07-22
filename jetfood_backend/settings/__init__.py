import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "development")

if DJANGO_ENV == "production":
    from .production import *
else:
    from .development import *
