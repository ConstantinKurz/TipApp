web: gunicorn tip_app.wsgi
worker: celery -A app/tip_app worker --pool=solo -l info
