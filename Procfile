% prepara el repositorio para su despliegue. 
release: sh -c 'cd TFG && python manage.py makemigrations && python manage.py migrate'
% especifica el comando para lanzar TFG
web: sh -c 'cd TFG && daphne -b 0.0.0.0 -p $PORT TFG.asgi:application'