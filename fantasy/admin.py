from django.contrib import admin

from .models import Equipo, Favoritos,Jugador, Plantilla,Stats,Valores

# Register your models here.
admin.site.register(Equipo)
admin.site.register(Jugador)
admin.site.register(Stats)
admin.site.register(Valores)
admin.site.register(Plantilla)
admin.site.register(Favoritos)
