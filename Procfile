% prepara el repositorio para su despliegue. 
release: sh -c 'python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput'
% especifica el comando para lanzar TFG
web: sh -c 'gunicorn TFG.wsgi --log-file -'