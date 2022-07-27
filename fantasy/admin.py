from django.contrib import admin

from .models import Equipo,Jugador,Stats,Valores

# Register your models here.
admin.site.register(Equipo)
admin.site.register(Jugador)
admin.site.register(Stats)
admin.site.register(Valores)
