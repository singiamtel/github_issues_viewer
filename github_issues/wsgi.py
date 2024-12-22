"""
WSGI config for github_issues project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'github_issues.settings')

application = get_wsgi_application() 