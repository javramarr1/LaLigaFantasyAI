from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from joblib import dump, load  # conda install -c anaconda joblib

import pandas as pd
import numpy as np
from io import StringIO
from django.db.models import Sum

from sklearn.neighbors import NearestNeighbors

from math import exp

from .forms import RegisterForm
from .scraping import almacena_jugador, estadisticas_bbdd
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Jugador,Stats,Valores

jugadores = Jugador.objects.all()
# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect(inicio)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)
        if user:
            login(request, user)
            return redirect(inicio)
        if user is None:
            return render(request,'login.html', {'no_user':True})
        
    return render(request,'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect(inicio)
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form_usuario = form.cleaned_data["username"]
            form_password = form.cleaned_data['password']
            form_correo = form.cleaned_data['correo']

            user = User.objects.create(username=form_usuario, email=form_correo)
            user.set_password(form_password)
            user.save()

            login(request, user)
            return redirect(inicio)
    return render(request,'registro.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect(inicio)

def inicio(request):
    j = sorted(jugadores,key=lambda t:-t.getPuntosTotales())
    p = Paginator(j,25)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    return render(request,'listado.html',{'jugadores':j,'page_obj':page_obj})

def carga_datos(request):
    nombres= []
    jugados=[]
    vals=[]
    mins=[]
    pts=[]
    for j in jugadores:
        totales = Stats.getTotalJugador(j.id)
        stats = Stats.objects.filter(jugador_id=j.id)
        d = len(stats)
        nombres.append(j.nombre)
        jugados.append(d)
        vals.append(Valores.objects.filter(jugador_id=j.id).aggregate(Sum('valor'))['valor__sum']/d)
        mins.append(totales['minutos__sum']/d)
        pts.append(j.getMediaPuntos())
        
    dict = {'nombre':nombres,'disputados':jugados,'minutos':mins,'puntos':pts,'valorMedio':vals}

    df = pd.DataFrame(data = dict)

    neigh = NearestNeighbors(n_neighbors=6)
    neigh.fit(df.drop(columns=['nombre']))
    dump(neigh,'fantasy/joblibs/knn/knn.joblib')

    # jugadores = almacena_jugador()
    # estadisticas_bbdd('TFG/fantasy/csv/porteros2122.csv')
    # estadisticas_bbdd('TFG/fantasy/csv/defensas2122.csv')
    # estadisticas_bbdd('TFG/fantasy/csv/medios2122.csv')
    # estadisticas_bbdd('TFG/fantasy/csv/delanteros2122.csv')
        
    return render(request,'listado.html')

def perfil_jugador(request,jugador_id):
    jugador = Jugador.objects.get(id = jugador_id)
    maxs = Stats.getMaximos()
    totales = Stats.getTotalJugador(jugador_id)

    #########################################################prediccion#####################################################################
    stats = Stats.objects.filter(jugador_id=jugador_id)
    disputados = len(stats)
    mediaValores = Valores.objects.filter(jugador_id=jugador_id).aggregate(Sum('valor'))['valor__sum']/disputados
    
    mediaMins = totales['minutos__sum']/disputados
    mediaPts = jugador.getMediaPuntos()  

    knn = load('fantasy/joblibs/knn/knn.joblib')
    sim = knn.kneighbors(np.array([disputados,mediaMins,mediaPts,mediaValores]).reshape(-1,4), return_distance = False)
    i=0
    s2= []
    for s in np.nditer(sim):       
        if i!=0:
            s2.append(jugadores[int(s)])
        i=1
    ##########################################################forma1modelo############################################################
    pos = jugador.posicion
    ultimas = stats[disputados-3].lineaVentana(pos)+','+stats[disputados-2].lineaVentana(pos)+','+stats[disputados-1].lineaVentana(pos)
    match pos:
        case "PO":
            modelo1j = load('fantasy/joblibs/1j/por-arbol-1j.joblib')
            modelo5j = load('fantasy/joblibs/5j/por-arbol-5j.joblib')
            modelo10j = load('fantasy/joblibs/10j/por-arbol-10j.joblib')
            linea = StringIO('pts_t-2,min_t-2,am_t-2,red_t-2,GC_t-2,par_t-2,v_t-2,pts_t-1,min_t-1,am_t-1,red_t-1,GC_t-1,par_t-1,v_t-1,pts_t,min_t,am_t,red_t,GC_t,par_t,v_t\n'+ultimas)
        case "DF":
            modelo1j = load('fantasy/joblibs/1j/def-arbol-1j.joblib')
            modelo5j = load('fantasy/joblibs/5j/def-arbol-5j.joblib')
            modelo10j = load('fantasy/joblibs/10j/def-arbol-10j.joblib')
            linea = StringIO('pts_t-2,min_t-2,am_t-2,red_t-2,rec_t-2,GC_t-2,v_t-2,pts_t-1,min_t-1,am_t-1,red_t-1,rec_t-1,GC_t-1,v_t-1,pts_t,min_t,am_t,red_t,rec_t,GC_t,v_t\n'+ultimas)
        case "MC":
            modelo1j = load('fantasy/joblibs/1j/med-arbol-1j.joblib')
            modelo5j = load('fantasy/joblibs/5j/med-arbol-5j.joblib')
            modelo10j = load('fantasy/joblibs/10j/med-arbol-10j.joblib')
            linea = StringIO('pts_t-2,min_t-2,am_t-2,red_t-2,asi_t-2,rec_t-2,v_t-2,pts_t-1,min_t-1,am_t-1,red_t-1,asi_t-1,rec_t-1,v_t-1,pts_t,min_t,am_t,red_t,asi_t,rec_t,v_t\n'+ultimas)
        case "DC":
            modelo1j = load('fantasy/joblibs/1j/dc-arbol-1j.joblib')
            modelo5j = load('fantasy/joblibs/5j/dc-arbol-5j.joblib')
            modelo10j = load('fantasy/joblibs/10j/dc-arbol-10j.joblib')
            linea = StringIO('pts_t-2,min_t-2,am_t-2,red_t-2,gol_t-2,asi_t-2,v_t-2,pts_t-1,min_t-1,am_t-1,red_t-1,gol_t-1,asi_t-1,v_t-1,pts_t,min_t,am_t,red_t,gol_t,asi_t,v_t\n'+ultimas)
    
    var = pd.read_csv(linea, sep=',')
    r1j=modelo1j.predict(var)
    r5j=modelo5j.predict(var)
    r10j=modelo10j.predict(var)

    return render(request,'perfilJugador.html',{'jugador':jugador,'maxs':maxs,'totales':totales,'sig_valor':float(r1j[0])
    ,'v1j':Jugador.valorDisplay(r1j[0]),'v5j':Jugador.valorDisplay(r5j[0]),'v10j':Jugador.valorDisplay(r10j[0]),'s2': s2})
    ##########################################################forma2forecasting############################################################
    # pred = []
    # serie = Valores.objects.filter(jugador_id=jugador_id).order_by("jornada")
    # for j in serie:
    #     pred.append(j.valor)

    # jornadas = 10
    # forecaster = ForecasterAutoreg(
    #     regressor = GradientBoostingRegressor(),
    #                 lags      = 3  #numero de jornadas pasadas en las que fijarse para predecir la información
    #             )

    # forecaster.fit(y=pd.Series(pred))
    # predicciones = forecaster.predict(steps=jornadas) #Numero de jornadas a futuro que se quiere predecir

    # return render(request,'perfilJugador.html',{'jugador':jugador,'maxs':maxs,'totales':totales,'sig_valor':float(predicciones.values[0])
    # ,'v1j':Jugador.valorDisplay(predicciones.values[0]),'v5j':Jugador.valorDisplay(predicciones.values[4]),'v10j':Jugador.valorDisplay(predicciones.values[9])})

def rankings(request):
    return render(request,'rankings.html')

@login_required(login_url="/login")
def mi_equipo(request,username):
    return render(request,'perfilUsuario.html')
