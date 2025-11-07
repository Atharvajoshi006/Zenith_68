"""
WSGI config for Adhyeta project.

This file exposes the WSGI callable as a module-level variable named ``application``.
It’s used by WSGI servers like Gunicorn or mod_wsgi to serve your Django application.

For more details, see:
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Ensure the correct settings module is loaded for WSGI servers
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adhyeta.settings")

application = get_wsgi_application()
