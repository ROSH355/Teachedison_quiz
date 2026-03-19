import os
from django.core.wsgi import get_wsgi_application

# Railway sets DJANGO_SETTINGS_MODULE via environment variables
# If not set, defaults to production
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'config.settings.production'
)

application = get_wsgi_application()