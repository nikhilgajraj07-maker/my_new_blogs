release: python manage.py migrate --noinput && python manage.py loaddata data.json
web: gunicorn project1.wsgi
