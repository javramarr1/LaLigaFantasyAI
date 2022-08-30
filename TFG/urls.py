"""TFG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from fantasy import views

urlpatterns = [
    path('admin/', admin.site.urls,name="admin"),
    path('',views.inicio,name="inicio"),
    path('cargarJugadores/',views.carga_jugadores,name="cargarJugadores"),
    path('cargarPorteros/',views.carga_porteros,name="cargarPorteros"),
    path('cargarDefensas1/',views.carga_defensas1,name="cargarDefensas"),
    path('cargarDefensas2/',views.carga_defensas2,name="cargarDefensas2"),
    path('cargarMedios1/',views.carga_medios1,name="cargarMedios1"),
    path('cargarMedios2/',views.carga_medios2,name="cargarMedios2"),
    path('cargarDelanteros1/',views.carga_delanteros1,name="cargarDelanteros1"),
    path('cargarDelanteros2/',views.carga_delanteros2,name="cargarDelanteros2"),
    path('cargarJoblib/',views.carga_joblib,name="cargarJoblib"),
    path('rankings/',views.rankings,name="rankings"),
    path('login/',views.login_view,name="login"),
    path('registro/',views.register_view,name="registro"),
    path('logout/',views.logout_view,name="logout"),
    path('perfil/<int:jugador_id>',views.perfil_jugador ,name="perfilJugador"),
    path('usuario/<slug:username>',views.mi_equipo ,name="equipoUsuario"),
    path('club/<int:club_id>',views.clubes ,name="clubes"),
]
