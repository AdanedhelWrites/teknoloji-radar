"""
Celery configuration for cybernews project.
"""

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybernews.settings')

app = Celery('cybernews')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
