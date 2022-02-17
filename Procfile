web: gunicorn tip_app.wsgi
#worker: celery -A tip_app worker --pool=solo -l info
celery: celery worker -A tip_app worker -B --loglevel=info