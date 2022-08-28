#encoding:utf-8
from datetime import datetime
import requests as r
import numpy as np
import pandas as pd
from math import log
from .models import Jugador,Equipo,Stats,Valores

#hay jugadores que han llegado a la liga más tarde por lo que los valores desde su primera fecha a la primera jornada van a salir
#negativos. Obviarlos hasta ver que se puede hacer con sus datos

#obtener las posiciones en las que se encuentran las fechas para los jugadores añadidos el 13 de julio
#para los jugadores que se han añadido en cualquier otra fecha ir recorriendo.

#restar los días entre fechas para calcular desplazamiento entre fechas y evitar que se recorran todas

####################################################################################################
#Calculo de los valores de mercado en cada una de las jornadas del jugador que se pasa como parametro
def calcula_valores(id):
    urlmarca = "https://api.laligafantasymarca.com/api/v3/player/"+str(id)+"/market-value?x-lang=es" #ya coge valores de la 22/23
    mercado = r.get(urlmarca).json()
    fechas = ["2021-08-17","2021-08-23","2021-08-30","2021-09-13","2021-09-20","2021-09-24","2021-09-27","2021-10-04","2021-10-18","2021-10-25",
    "2021-10-28","2021-11-01","2021-11-08","2021-11-22","2021-11-29","2021-12-06","2021-12-13","2021-12-20","2022-01-03","2022-01-10",
    "2022-01-17","2022-01-24","2022-02-07","2022-02-14","2022-02-21","2022-02-28","2022-03-07","2022-03-14","2022-03-21","2022-04-04",
    "2022-04-11","2022-04-18","2022-04-21","2022-05-02","2022-05-09","2022-05-12","2022-05-16","2022-05-23"]
    jornadas = []
    for fecha in fechas:
        f = datetime.strptime(fecha,"%Y-%m-%d").date()
        if f>datetime.now().date():
            break
        for m in mercado:
            encuentra = False
            indice = 0
            if datetime.fromisoformat(m['date']).date()==f:
                indice = mercado.index(m)
                encuentra= True
                break
        if not encuentra or indice<0:
            jornadas.append(np.nan)
        else:
            jornadas.append(mercado[indice]['marketValue'])
        mercado = mercado[indice:]
    return pd.Series(jornadas).interpolate()

####################################################################################################
#Creacion de las líneas del dataset en función de las variables utilizadas por posición
def crea_lineas(v,v_mercado,var1,var2):
    puntuaciones=v["playerStats"]
    p_totales=puntuaciones[0].get('values')

    jornadas_disputadas = v['weeks']
    x1 = [0]*len(jornadas_disputadas)
    x2 = [0]*len(jornadas_disputadas)
    amarillas= [0]*len(jornadas_disputadas)
    rojas = [0]*len(jornadas_disputadas)
    
    for punt in puntuaciones:   
        if(punt.get('value')=="total_mins_played"):
            minutos_jugados = punt.get('values')
        if(punt.get('value')=="total_yellow_card"):
            amarillas=punt.get('values')
        if(punt.get('value')==var1):
            x1 = punt.get('values')
        if(punt.get('value')==var2):
            x2 = punt.get('values')
        if(punt.get('value')=="total_red_card"):
            rojas = punt.get('values')
        

    listado = list(zip(p_totales,minutos_jugados,amarillas,rojas,x1,x2))
    datos = dict(zip(jornadas_disputadas,listado))
    
    tarjetas = 0
    i=1
    for i in range(1,v['jornadaActiva']+1):
        valor = v_mercado[i-1]
        if not pd.isna(valor):
            if not i in datos:
                datos[i]=[i,0,0,0,0,0,0,log(valor)]   
            else:
                if datos[i][2]==1:
                    tarjetas += 1
                    datos[i]=[i,datos[i][0],datos[i][1],tarjetas,datos[i][3],datos[i][4],datos[i][5],log(valor)]
                else:
                    datos[i]=[i,datos[i][0],datos[i][1],0,datos[i][3],datos[i][4],datos[i][5],log(valor)]
            if tarjetas == 5:
                tarjetas = 0

        #Si al jugador se le ha colado info con valores de mercado nulos se eliminan (no se añaden ni ceros)
        else:
            if i in datos:
                del datos[i]            
        i+=1  
    return datos

####################################################################################################

def crea_lineas_completas(v,v_mercado):
    puntuaciones=v["playerStats"]
    p_totales=puntuaciones[0].get('values')

    jornadas_disputadas = v['weeks']
    n = len(jornadas_disputadas)
    amarillas=rojas=goles=asist=asistSinGol=paradas=centros=despejes=penFallados=encajados=tiros=regates=recuperaciones=perdidas=ptsMarca=[0]*n
    
    for punt in puntuaciones:   
        if(punt.get('value')=="total_mins_played"):
            minutos_jugados = punt.get('values')
        if(punt.get('value')=="total_yellow_card"):
            amarillas=punt.get('values')
        if(punt.get('value')=="total_red_card"):
            rojas = punt.get('values')
        if(punt.get('value')=="total_goals"):
            goles = punt.get('values')
        if(punt.get('value')=="total_goal_assist"):
            asist = punt.get('values')
        if(punt.get('value')=="total_offtarget_att_assist"):
            asistSinGol = punt.get('values')
        if(punt.get('value')=="total_pen_area_entries"):
            centros = punt.get('values')
        if(punt.get('value')=="total_effective_clearance"):
            despejes = punt.get('values')
        if(punt.get('value')=="total_penalty_failed"):
            penFallados = punt.get('values')
        if(punt.get('value')=="total_goals_conceded"):
            encajados = punt.get('values')
        if(punt.get('value')=="total_total_scoring_att"):
            tiros = punt.get('values')
        if(punt.get('value')=="total_won_contest"):
            regates = punt.get('values')
        if(punt.get('value')=="total_ball_recovery"):
            recuperaciones = punt.get('values')
        if(punt.get('value')=="total_poss_lost_all"):
            perdidas = punt.get('values')
        if(punt.get('value')=="score_marca_points"):
            ptsMarca  = punt.get('values')
        

    listado = list(zip(p_totales,minutos_jugados,amarillas,rojas,goles,asist,asistSinGol,paradas,centros,despejes,penFallados,encajados,tiros,regates,recuperaciones,perdidas,ptsMarca))
    datos = dict(zip(jornadas_disputadas,listado))
    
    tarjetas = 0
    i=1
    for i in range(1,v['jornadaActiva']+1):
        valor = v_mercado[i-1]
        if not pd.isna(valor):
            
            #Si no se encuentra la jornada, puntuaciones a 0
            if not i in datos:
                datos[i]=[0]*17
            
            else:
                datos [i] = list(datos[i])
                if datos[i][2]==1:
                    datos[i][2] += 1

                    #aqui hay un fallooooooo, se corrige de momento dividiendo las stats en el model entre 2
                    
                else:
                    datos[i][2] = 0
            if tarjetas == 5:
                tarjetas = 0
            datos[i].insert(0,i)
            datos[i].append(valor)
        else:
            if i in datos:
                del datos[i]            
        i+=1  
    return datos
####################################################################################################

def escribe_csv(v,nombre,id,fichero,equipo,variable1,variable2,completo):
    if completo:
        datos = crea_lineas_completas(v,calcula_valores(v['playerId']))
    else:
        datos = crea_lineas(v,calcula_valores(v['playerId']),variable1,variable2)
    for p in sorted(datos.items()):
        fichero.write(nombre + "," + id +","+ equipo + "," + ",".join(map(str,p[1])) + "\n")

#####################################################################################################

def csv_listado(jugadores,temporada):
    
    por = open('TFG/fantasy/csv/'+temporada+'/porteros.csv', 'w',encoding='utf-8')
    df = open('TFG/fantasy/csv/'+temporada+'/defensas.csv', 'w',encoding='utf-8')
    med = open('TFG/fantasy/csv/'+temporada+'/medios.csv', 'w',encoding='utf-8')
    dc = open('TFG/fantasy/csv/'+temporada+'/delanteros.csv', 'w',encoding='utf-8')
    jug = open('TFG/fantasy/csv/'+temporada+'/listado.csv', 'w',encoding='utf-8')

    por.write("Nombre,id,Equipo,Jornada,Puntos,Minutos,amarillas,rojas,goles,asist,asistSinGol,paradas,centros,despejes,penFallados,encajados,tiros,regates,recuperaciones,perdidas,ptsMarca,Valor\n")
    df.write("Nombre,id,Equipo,Jornada,Puntos,Minutos,amarillas,rojas,goles,asist,asistSinGol,paradas,centros,despejes,penFallados,encajados,tiros,regates,recuperaciones,perdidas,ptsMarca,Valor\n")
    med.write("Nombre,id,Equipo,Jornada,Puntos,Minutos,amarillas,rojas,goles,asist,asistSinGol,paradas,centros,despejes,penFallados,encajados,tiros,regates,recuperaciones,perdidas,ptsMarca,Valor\n")
    dc.write("Nombre,id,Equipo,Jornada,Puntos,Minutos,amarillas,rojas,goles,asist,asistSinGol,paradas,centros,despejes,penFallados,encajados,tiros,regates,recuperaciones,perdidas,ptsMarca,Valor\n")

    for jugador in jugadores:
        slug = jugador['slug']
        nombre = jugador['nn']
        equipo = jugador['tn']
        urlaf = "https://analitica-fantasy.azurewebsites.net/api/lfmPlayers/playerAnalisisSlug?slug="+slug+"&season=2021"
        v = r.get(urlaf).json()
        id = str(v['playerId'])
        print(nombre + " (" + id + ")")

        jug.write(str(id)+","+str(nombre)+","+str(v['playerStatus'])+","+str(v['positionId'])+","+str(equipo)+"\n")

        #equipo = v['teamSlug'].replace("-"," ").title() 
        
        #nombre + "," + str(p[1][0]) + "," + str(p[1][1]) + "," + str(p[1][2])  + "," + str(p[1][3]) + "," + str(p[1][4]) + "," + str(p[1][5]) + "\n"
 
        match v['positionId']:
            case 1:
               escribe_csv(v,nombre,id,por,equipo,"total_goals_conceded","total_saves",True)
            case 2:
                escribe_csv(v,nombre,id,df,equipo,"total_ball_recovery","total_goals_conceded",True)
            case 3:
                escribe_csv(v,nombre,id,med,equipo,"total_goal_assist","total_ball_recovery",True)            
            case 4:
                escribe_csv(v,nombre,id,dc,equipo,"total_goals","total_goal_assist",True)  

    jug.close()
    por.close()
    df.close()
    med.close()
    dc.close()

##################################################################################################

def ventanas(leer, escribir,header):

    fleer = open(leer,"rt")
    fescribir = open(escribir,"w")

    fescribir.write(header + "\n")

    csv = fleer.readlines()

    i = 1  
    for i in range(0,len(csv)-3):
        nombre = csv[i].split(",")[0]
        nombre_sig = csv[i+3].split(",")[0]
        if(nombre==nombre_sig):
            t_2=csv[i].replace(nombre + "," + csv[i].split(",")[1] +",","").strip("\n")
            t_1=csv[i+1].replace(nombre + ","+ csv[i+1].split(",")[1] +",","").strip("\n")
            t=csv[i+2].replace(nombre + ","+ csv[i+2].split(",")[1] +",","").strip("\n")
            test=csv[i+3].split(",")[6].strip("\n")
            fescribir.write(str(t_2) + "," + str(t_1) + "," + str(t) + "," + str(test) + "\n")
            i+=1
        else:
            i+=4

    fleer.close()
    fescribir.close()

##################################################################################################

def jugadores():
    url= "https://analitica-fantasy.azurewebsites.net/api/lfmPlayers/playersStats?temporada=2021&jornadaActiva=-1"
    lista_jugadores = r.get(url)
    json = lista_jugadores.json()
    temporada = "2122"

    csv_listado(json['players'],temporada)

##################################################################################################

def almacena_jugador():
    url= "https://analitica-fantasy.azurewebsites.net/api/lfmPlayers/playersStats?temporada=2021&jornadaActiva=-1"
    lista_jugadores = r.get(url)
    json = lista_jugadores.json()

    jug = open('TFG/fantasy/csv/listado2122.csv', 'w',encoding='utf-8')

    for jugador in json['players']:
        equipo = Equipo.objects.get_or_create(nombre = jugador["tn"])
        estado = "Pretemporada" if not jugador['pss'] else jugador['pss']
        match jugador["pid"]:
            case 1:
                posicion = "PO"
            case 2:
                posicion = "DF"
            case 3:
                posicion = "MC"         
            case 4:
                posicion = "DC"

        Jugador.objects.get_or_create(id= jugador['playerId'],nombre = jugador['nn'],estado = estado,posicion = posicion,equipo = equipo[0])
        
        jug.write(str(jugador['playerId'])+","+jugador['nn']+","+estado+","+posicion+","+str(jugador["tn"])+"\n")

    jug.close()


##################################################################################################ç

def leer_jugadores(fichero):

    f = open(fichero,"rt",encoding='utf-8')
    csv = f.readlines()   

    i = 0

    for i in range(0,len(csv)):

        jugador = csv[i].split(",")
        equipo = Equipo.objects.get_or_create(nombre=jugador[4])
        Jugador.objects.get_or_create(id= int(jugador[0]),nombre = jugador[1],estado = jugador[2],posicion = jugador[3],equipo = equipo[0])
        i+=1

    f.close()

##################################################################################################

def estadisticas_bbdd(fichero,section,sec):

    f = open(fichero,"rt",encoding='utf-8')
    csv = f.readlines()

    if section:

        if sec==1 :
            i = 1
            size = len(csv)/2
        else:
            i = len(csv)/2
            size = len(csv)       

        for i in range(i,size):
            jornada = csv[i].split(",")
            id = int(jornada[1])
            n_jor = int(jornada[3])
            try:
                jugador = Jugador.objects.get(id=id)
                Stats.objects.get_or_create(jugador_id=jugador,jornada = n_jor,puntos = int(jornada[4]),minutos = int(jornada[5]),goles = int(jornada[8]),asist = int(jornada[9]), asistSinGol = int(jornada[10]),
                paradas = int(jornada[11]),amarillas = int(jornada[6]),rojas = int(jornada[7]), centros = int(jornada[12]),despejes = int(jornada[13]),penFallados = int(jornada[14]),
                encajados = int(jornada[15]),tiros = int(jornada[16]),regates = int(jornada[17]),recuperaciones = int(jornada[18]),perdidas = int(jornada[19]),ptsMarca = int(jornada[20]))

                Valores.objects.get_or_create(jugador_id = jugador,jornada = n_jor,valor = float(jornada[21]))
            except Jugador.DoesNotExist:
                i+=1
    
    else:
        i = 1

        for i in range(1,len(csv)):
            jornada = csv[i].split(",")
            id = int(jornada[1])
            n_jor = int(jornada[3])
            try:
                jugador = Jugador.objects.get(id=id)
                Stats.objects.get_or_create(jugador_id=jugador,jornada = n_jor,puntos = int(jornada[4]),minutos = int(jornada[5]),goles = int(jornada[8]),asist = int(jornada[9]), asistSinGol = int(jornada[10]),
                paradas = int(jornada[11]),amarillas = int(jornada[6]),rojas = int(jornada[7]), centros = int(jornada[12]),despejes = int(jornada[13]),penFallados = int(jornada[14]),
                encajados = int(jornada[15]),tiros = int(jornada[16]),regates = int(jornada[17]),recuperaciones = int(jornada[18]),perdidas = int(jornada[19]),ptsMarca = int(jornada[20]))

                Valores.objects.get_or_create(jugador_id = jugador,jornada = n_jor,valor = float(jornada[21]))
            except Jugador.DoesNotExist:
                i+=1

    f.close()
'''
def calendario():
    i=1
    while i<=38:
        url = "https://es.besoccer.com/competicion/clasificacion/primera/2022/jornada" + str(i)


ventanas('porteros.csv','por_ventana.csv',
'pts_t-2,min_t-2,am_t-2,red_t-2,GC_t-2,par_t-2,v_t-2,pts_t-1,min_t-1,am_t-1,red_t-1,GC_t-1,par_t-1,v_t-1,pts_t,min_t,am_t,red_t,GC_t,par_t,v_t,v_test')
ventanas('defensas.csv','def_ventana.csv',
'pts_t-2,min_t-2,am_t-2,red_t-2,rec_t-2,GC_t-2,v_t-2,pts_t-1,min_t-1,am_t-1,red_t-1,rec_t-1,GC_t-1,v_t-1,pts_t,min_t,am_t,red_t,rec_t,GC_t,v_t,v_test')
ventanas('medios.csv','med_ventana.csv',
'pts_t-2,min_t-2,am_t-2,red_t-2,asi_t-2,rec_t-2,v_t-2,pts_t-1,min_t-1,am_t-1,red_t-1,asi_t-1,rec_t-1,v_t-1,pts_t,min_t,am_t,red_t,asi_t,rec_t,v_t,v_test')
ventanas('delanteros.csv','dc_ventana.csv',
'pts_t-2,min_t-2,am_t-2,red_t-2,gol_t-2,asi_t-2,v_t-2,pts_t-1,min_t-1,am_t-1,red_t-1,gol_t-1,asi_t-1,v_t-1,pts_t,min_t,am_t,red_t,gol_t,asi_t,v_t,v_test')
'''