web: gunicorn tip_app.wsgi
worker: celery worker -A tip_app -l INFO --pool=solo
beat:  celery -A tip_app worker -B