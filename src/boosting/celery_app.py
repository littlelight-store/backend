import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boosting.settings')

app = Celery('boosting')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

print(app)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
