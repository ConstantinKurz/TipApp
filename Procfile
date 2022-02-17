web: gunicorn tip_app.wsgi
worker: celery worker -A tip_app.app -l INFO
beat:  celery -A tip_app.app worker -B