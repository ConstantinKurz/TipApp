web: gunicorn tip_app.wsgi
worker: celery -A tip_app worker --loglevel=info --beat