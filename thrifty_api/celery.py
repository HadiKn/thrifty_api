import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thrifty_api.settings')

app = Celery('thrifty_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Schedule for auction ending
app.conf.beat_schedule = {
    'end-expired-auctions': {
        'task': 'items.tasks.end_expired_auctions',
        'schedule': crontab(minute='*'),  # Every minute
    },
}