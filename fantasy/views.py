from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .scraping import almacena_jugador, estadisticas_bbdd
from django.core.paginator import Paginator

from .models import Jugador,Valores,Stats

# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect(inicio)
    if request.method == 'POST':
        username = request.post['username']
        password = request.post['pass']
        user = authenticate(username = username, password = password)
        if user:
            login(request, user)
            return redirect(inicio)
    return render(request,'login.html')

def register_view(request):
    return render(request,'registro.html')

def logout_view(request):
    logout(request)
    return redirect(inicio)

def inicio(request):
    jugadores = Jugador.objects.all()
    p = Paginator(jugadores,25)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    return render(request,'listado.html',{'jugadores':jugadores,'page_obj':page_obj})

def carga_datos(request):
    jugadores = almacena_jugador()
    estadisticas_bbdd('TFG/fantasy/csv/porteros2122.csv')
    estadisticas_bbdd('TFG/fantasy/csv/defensas2122.csv')
    estadisticas_bbdd('TFG/fantasy/csv/medios2122.csv')
    estadisticas_bbdd('TFG/fantasy/csv/delanteros2122.csv')
        
    return render(request,'listado.html',{'jugadores':jugadores})

def perfil_jugador(request,jugador_id):
    jugador = Jugador.objects.get(id = jugador_id)
    maxs = Stats.getMaximos()
    totales = Stats.getTotalJugador(jugador_id)
    return render(request,'perfilJugador.html',{'jugador':jugador,'maxs':maxs,'totales':totales})

def rankings(request):
    return render(request,'rankings.html')
