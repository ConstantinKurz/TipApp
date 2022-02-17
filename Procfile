web: gunicorn tip_app.wsgi
worker: celery -A tip_app worker --pool=solo -l info
beat: celery -A tip_app beat -l INFO