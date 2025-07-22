"""
WSGI config for ig_prj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""


import os
import sys

path = '/home/rahima123/university/Instagram-Clone-master'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ig_pij.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
