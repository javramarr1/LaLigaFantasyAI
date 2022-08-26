% prepara el repositorio para su despliegue. 
release: sh -c 'python manage.py migrate'
% especifica el comando para lanzar MakeAMate
web: sh -c 'gunicorn TFG.wsgi --log-file -'