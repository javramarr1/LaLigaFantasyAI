from itertools import count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from joblib import dump, load  # conda install -c anaconda joblib

import pandas as pd
import numpy as np
from io import StringIO
from django.db.models import Sum,Count

from sklearn.neighbors import NearestNeighbors

from math import exp

from .forms import RegisterForm, accionesJugadorForm, addJugadorForm
from .scraping import almacena_jugador, estadisticas_bbdd
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core import serializers

from .models import Equipo, Jugador,Stats,Valores, Plantilla, Favoritos

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

            Plantilla.objects.create(user=user)
            Favoritos.objects.create(user=user)

            login(request, user)
            return redirect(inicio)
    return render(request,'registro.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect(inicio)

def inicio(request):
    jug = serializers.serialize("json", jugadores)
    params = {}
    if request.user.is_authenticated:
        plantilla = Plantilla.objects.get_or_create(user=User.objects.get(username=request.user.username))[0]
        fav = Favoritos.objects.get_or_create(user=User.objects.get(username=request.user.username))[0]

        form = formulario(request,plantilla,fav)
        params['form'] = form
        params['plantilla'] = plantilla.jugadores.all()
        params['favs'] = fav.jugadores.all()

    j = sorted(jugadores,key=lambda t:-t.getPuntosTotales())
    p = Paginator(j,25)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    params.update({'jugadores':j,'page_obj':page_obj,'jug':jug})
    return render(request,'listado.html',params)

def carga_datos(request):
    nombres,jugados,vals,mins,pts= [],[],[],[],[]
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
    
    valores = Valores.objects.filter(jugador_id=jugador_id)
    labels = [str(x.jornada) for x in valores.order_by('jornada')]
    dataset = [int(exp(x.valor)) for x in valores.order_by('jornada')]
    #########################################################prediccion#####################################################################
    stats = Stats.objects.filter(jugador_id=jugador_id)
    disputados = len(stats)
    mediaValores = valores.aggregate(Sum('valor'))['valor__sum']/disputados
    
    mediaMins = totales['minutos__sum']/disputados
    mediaPts = jugador.getMediaPuntos()  

    knn = load('fantasy/joblibs/knn/knn.joblib')
    sim = knn.kneighbors(np.array([disputados,mediaMins,mediaPts,mediaValores]).reshape(-1,4), return_distance = False)
    i,s2=0,[]
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

    params= {'jugador':jugador,'maxs':maxs,'totales':totales,'sig_valor':float(r1j[0]),'labels':labels,'dataset':dataset
    ,'v1j':Jugador.valorDisplay(r1j[0],True),'v5j':Jugador.valorDisplay(r5j[0],True),'v10j':Jugador.valorDisplay(r10j[0],True),'s2': s2}

    if request.user.is_authenticated:
        plantilla = Plantilla.objects.get(user=request.user)
        favs = Favoritos.objects.get(user=request.user)
        params['plantilla']=plantilla.jugadores.all()
        params['favs']=favs.jugadores.all()
        form = addJugadorForm()
        params['form']=form    
        if request.method == 'POST':
            form = addJugadorForm(request.POST)
            if form.is_valid():
                
                equipo = form.cleaned_data.get("addSquad")
                fav = form.cleaned_data.get("addFavs")

                if equipo == "Añadir a mi equipo":
                    plantilla.jugadores.add(jugador)
                elif equipo == "Eliminar de mi equipo" and checkIn(plantilla,jugador_id):
                    plantilla.jugadores.remove(jugador)
                
                if fav == "Añadir a favoritos":
                    favs.jugadores.add(jugador)
                elif fav == "Eliminar de favoritos" and checkIn(favs,jugador_id):
                    favs.jugadores.remove(jugador)

                plantilla.save()
                favs.save()

    return render(request,'perfilJugador.html',params)
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

def formulario(request,plantilla,fav):
    form = accionesJugadorForm()
    if request.method == "POST":
        form = accionesJugadorForm(request.POST)
        if form.is_valid():
            icon = form.cleaned_data.get("icon")
            jugador = form.cleaned_data.get("jug")
            tipo = form.cleaned_data.get("tipo")
            if icon:
                if tipo == "addSquad":
                    plantilla.jugadores.add(jugador) 
                elif tipo == "addFavs":
                    fav.jugadores.add(jugador)
                elif tipo == "delSquad" and checkIn(plantilla,jugador):
                    plantilla.jugadores.remove(jugador)
                elif tipo == "delFavs" and checkIn(fav,jugador):
                    fav.jugadores.remove(jugador)
                plantilla.save()
                fav.save()
    return form

def checkIn(obj,idJugador):
    return True if Jugador.objects.get(id = idJugador) in obj.jugadores.all() else False

def rankings(request):
    stats,goleadores,minutos,ptsMarca,amarillas,porCero,rentabilidad = {},{},{},{},{},{},{}
    for g in Stats.objects.values('jugador_id').annotate(Sum('goles')).order_by('-goles__sum')[0:5]:
        jug = Jugador.objects.get(id=g['jugador_id'])
        goleadores[jug]=g['goles__sum']
    
    for g in Stats.objects.values('jugador_id').annotate(Sum('minutos')).order_by('-minutos__sum')[0:5]:
        jug = Jugador.objects.get(id=g['jugador_id'])
        minutos[jug]=g['minutos__sum']

    for g in Stats.objects.values('jugador_id').annotate(Sum('ptsMarca')).order_by('-ptsMarca__sum')[0:5]:
        jug = Jugador.objects.get(id=g['jugador_id'])
        ptsMarca[jug]=g['ptsMarca__sum']

    for g in Stats.objects.values('jugador_id').annotate(amarillas__sum = Sum('amarillas')/2).order_by('-amarillas__sum')[0:5]:
        jug = Jugador.objects.get(id=g['jugador_id'])
        amarillas[jug]=g['amarillas__sum']

    for g in Stats.objects.values('jugador_id').filter(minutos__gt = 60,encajados=0).annotate(total= Count('jugador_id')).order_by('-total')[0:5]:
        jug = Jugador.objects.get(id=g['jugador_id'])
        porCero[jug]=g['total']
    for g in jugadores:
        r = round(g.getPuntosTotales()*10000/int(exp(g.getValorActual())),3)
        rentabilidad[g] = r
    renta = sorted(rentabilidad.items(), key=lambda item: item[1],reverse=True)

    stats['Goleadores']=goleadores
    stats['Más minutos disputados']=minutos
    stats['Mejor valorados - Puntos Marca']=ptsMarca
    stats['Más amonestados']=amarillas
    stats['Porterías a cero']=porCero
    stats['Jugadores más rentables']=dict((x, y) for x, y in renta[0:5])
    return render(request,'rankings.html',{'stats':stats})

def clubes(request,club_id):
    equipo = Equipo.objects.filter(id=club_id)[0]
    club = Jugador.objects.filter(equipo=equipo)
    params = {'equipo':equipo,'club':club}
    if request.user.is_authenticated:
        plantilla = Plantilla.objects.get_or_create(user=User.objects.get(username=request.user.username))[0]
        fav = Favoritos.objects.get_or_create(user=User.objects.get(username=request.user.username))[0]
        form = formulario(request,plantilla,fav)
        params['form']=form
        params['plantilla']=plantilla.jugadores.all()
        params['favs']=fav.jugadores.all()
    return render(request,'clubes.html',params)

@login_required(login_url="/login")
def mi_equipo(request,username):
    plantilla = Plantilla.objects.get_or_create(user=User.objects.get(username=username))[0]
    fav = Favoritos.objects.get_or_create(user=User.objects.get(username=username))[0]

    form = formulario(request,plantilla,fav)

    j = plantilla.jugadores.all()

    por,df,med,dc,valorTotal,pts,warning = [],[],[],[],0,0,0

    for p in j:
        if p.estado == "Sancionado" or p.estado == "Lesionado":
            warning += 1
        valorTotal += int(exp(p.getValorActual()))
        pts += p.getMediaPuntos()
        match p.posicion:
            case "PO":
                por.append(p)
            case "DF":
                df.append(p)
            case "MC":
                med.append(p)
            case "DC":
                dc.append(p)

    total = len(j)
    if total:
        pts = round(pts/total,2)
    
    vt = Jugador.valorDisplay(valorTotal, False) if Jugador.valorDisplay(valorTotal, False) else 0
    print(j)

    params = {'plantilla':j,'fav':fav.jugadores.all(),'por':por,'df':df,'med':med,'dc':dc,
    'valorTotal':vt,'mediaPts':pts,'total':total, 'warning': warning, 'form':form}

    return render(request,'perfilUsuario.html',params)
