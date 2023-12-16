import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PIB_data_scrapper.settings")
app = Celery("PIB_data_scrapper")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
from celery.schedules import crontab
from celery.schedules import timedelta

# django_celery/settings.py

# ...

# app.conf.beat_schedule = {
#     "scrap_youtube_data": {
#         # "task": "api.tasks.scrap_youtube_data",
#         # "task": "newsgatherers.tasks.scrap_news_data",
#         # "schedule": crontab(minute="*/1"),
#         # 'schedule': crontab(hour='*/1'),
#     },
# }