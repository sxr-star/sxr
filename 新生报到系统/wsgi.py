"""
WSGI config for 新生报到系统 project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '新生报到系统.settings')

application = get_wsgi_application()
