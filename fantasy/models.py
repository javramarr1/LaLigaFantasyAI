from django.db import models
from math import exp,log
from django.db.models import Sum,Max
from django.contrib.auth.models import User

# Create your models here.

class Equipo(models.Model):
    # A ver si el equipo se puede meter como campo en el jugador o mejor se deja fuera
    id = models.PositiveSmallIntegerField(default=1)
    nombre = models.CharField(max_length=50,primary_key=True)
    
    def __str__(self):
        return self.nombre

class Jugador(models.Model):
    #Datos generales de los jugadores y sus relaciones: equipos, estadísticas
    #Incluir un id para cada uno?
    id = models.PositiveSmallIntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=50,blank=True)
    posicion = models.CharField(max_length=50)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)

    def getValorActual(self):
        return Valores.getLastValor(self.id)
    
    def getValorActualDisplay(self):
        v = str(int(exp(self.getValorActual())))
        match len(v):
            case 6:
                return v[0]+v[1]+v[2] + "." + v[3]+v[4]+v[5] + " €"
            case 7:
                return v[0] + "." +v[1]+v[2]+v[3] + "." + v[4]+v[5]+v[6] + " €"
            case 8:
                return v[0]+v[1]+ "." +v[2]+v[3]+v[4] + "." + v[5]+v[6]+v[7] + " €"
            case 9:
                return v[0]+v[1]+v[2] + "." +v[3]+v[4]+v[5] + "." + v[6]+v[7]+v[8] + " €"
    
    def valorDisplay(valor,expo):
        if expo:
            v= str(int(exp(valor)))
        else:
            v = str(valor)
        match len(v):
            case 6:
                return v[0]+v[1]+v[2] + "." + v[3]+v[4]+v[5] + " €"
            case 7:
                return v[0] + "." +v[1]+v[2]+v[3] + "." + v[4]+v[5]+v[6] + " €"
            case 8:
                return v[0]+v[1]+ "." +v[2]+v[3]+v[4] + "." + v[5]+v[6]+v[7] + " €"
            case 9:
                return v[0]+v[1]+v[2] + "." +v[3]+v[4]+v[5] + "." + v[6]+v[7]+v[8] + " €"

    def getPuntosTotales(self):
        return Stats.objects.filter(jugador_id=self.id).aggregate(Sum('puntos'))['puntos__sum']

    def jugados(self):
        return Stats.objects.filter(jugador_id=self.id).exclude(minutos=0).count()

    def getMediaPuntos(self):
        jugador = Stats.objects.filter(jugador_id=self.id)
        #solo las jornadas que han jugado o se hace la media sobre todas?
        jornadas = jugador.exclude(minutos=0).count()
        return round(jugador.aggregate(Sum('puntos'))['puntos__sum']/jornadas,2)

    # def addToPlantilla(self):
    #     jugadores.append(self)
    #     Plantilla.objects.update(user=)

    def __str__(self):
        return self.nombre

class Stats(models.Model):
    jugador_id = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    jornada = models.SmallIntegerField()
    puntos = models.SmallIntegerField()
    minutos = models.SmallIntegerField()
    goles = models.SmallIntegerField()
    asist = models.SmallIntegerField()
    asistSinGol = models.SmallIntegerField()
    paradas = models.SmallIntegerField()
    amarillas = models.SmallIntegerField()
    rojas = models.SmallIntegerField()
    centros = models.SmallIntegerField()
    despejes = models.SmallIntegerField()
    penFallados = models.SmallIntegerField()
    encajados = models.SmallIntegerField()
    tiros = models.SmallIntegerField()
    regates = models.SmallIntegerField()
    recuperaciones = models.SmallIntegerField()
    perdidas = models.SmallIntegerField()
    ptsMarca = models.SmallIntegerField()

    def lineaVentana(self, posicion):
        valor = Valores.objects.filter(jugador_id = self.jugador_id,jornada=self.jornada)[0]
        cadena = str(self.puntos) + ',' + str(self.minutos) + ',' + str(self.amarillas) + ',' + str(self.rojas)
        if posicion == 'PO':
            cadena += ',' + str(self.encajados) + ',' + str(self.paradas) + ',' + str(valor)
        elif posicion == 'DF':
            cadena += ',' + str(self.recuperaciones) + ',' + str(self.encajados) + ',' + str(valor)
        elif posicion == 'MC':
            cadena += ',' + str(self.asist) + ',' + str(self.recuperaciones) + ',' + str(valor)
            
        else:
            cadena += ',' + str(self.goles) + ',' + str(self.asist) + ',' + str(valor)
        
        return cadena

    def getTotalJugador(id):
        puntos = Stats.objects.filter(jugador_id=id).aggregate(Sum('puntos'))
        minutos = Stats.objects.filter(jugador_id=id).aggregate(Sum('minutos'))
        goles = Stats.objects.filter(jugador_id=id).aggregate(Sum('goles'))
        asist = Stats.objects.filter(jugador_id=id).aggregate(Sum('asist'))
        asistSinGol = Stats.objects.filter(jugador_id=id).aggregate(Sum('asistSinGol'))
        paradas = Stats.objects.filter(jugador_id=id).aggregate(Sum('paradas'))
        amarillas = Stats.objects.filter(jugador_id=id).aggregate(amarillas__sum = Sum('amarillas')/2)
        rojas = Stats.objects.filter(jugador_id=id).aggregate(Sum('rojas'))
        centros = Stats.objects.filter(jugador_id=id).aggregate(Sum('centros'))
        despejes = Stats.objects.filter(jugador_id=id).aggregate(Sum('despejes'))
        penFallados = Stats.objects.filter(jugador_id=id).aggregate(Sum('penFallados'))
        encajados = Stats.objects.filter(jugador_id=id).aggregate(Sum('encajados'))
        tiros = Stats.objects.filter(jugador_id=id).aggregate(Sum('tiros'))
        regates = Stats.objects.filter(jugador_id=id).aggregate(Sum('regates'))
        recuperaciones = Stats.objects.filter(jugador_id=id).aggregate(Sum('recuperaciones'))
        perdidas = Stats.objects.filter(jugador_id=id).aggregate(Sum('perdidas'))
        ptsMarca = Stats.objects.filter(jugador_id=id).aggregate(Sum('ptsMarca'))
        total = puntos|minutos|goles|asist|asistSinGol|paradas|amarillas|rojas|centros|despejes|penFallados|encajados|tiros|regates|recuperaciones|perdidas|ptsMarca
        return total

   
    def getMaximos():
        puntos = Stats.objects.values('jugador_id').annotate(Sum('puntos')).order_by('-puntos__sum')[0]
        minutos = Stats.objects.values('jugador_id').annotate(Sum('minutos')).order_by('-minutos__sum')[0]
        goles = Stats.objects.values('jugador_id').annotate(Sum('goles')).order_by('-goles__sum')[0]
        asist = Stats.objects.values('jugador_id').annotate(Sum('asist')).order_by('-asist__sum')[0]
        asistSinGol = Stats.objects.values('jugador_id').annotate(Sum('asistSinGol')).order_by('-asistSinGol__sum')[0]
        paradas = Stats.objects.values('jugador_id').annotate(Sum('paradas')).order_by('-paradas__sum')[0]
        amarillas = Stats.objects.values('jugador_id').annotate(amarillas__sum = Sum('amarillas')/2).order_by('-amarillas__sum')[0]
        rojas = Stats.objects.values('jugador_id').annotate(Sum('rojas')).order_by('-rojas__sum')[0]
        centros = Stats.objects.values('jugador_id').annotate(Sum('centros')).order_by('-centros__sum')[0]
        despejes = Stats.objects.values('jugador_id').annotate(Sum('despejes')).order_by('-despejes__sum')[0]
        penFallados = Stats.objects.values('jugador_id').annotate(Sum('penFallados')).order_by('-penFallados__sum')[0]
        encajados = Stats.objects.values('jugador_id').annotate(Sum('encajados')).order_by('-encajados__sum')[0]
        tiros = Stats.objects.values('jugador_id').annotate(Sum('tiros')).order_by('-tiros__sum')[0]
        regates = Stats.objects.values('jugador_id').annotate(Sum('regates')).order_by('-regates__sum')[0]
        recuperaciones = Stats.objects.values('jugador_id').annotate(Sum('recuperaciones')).order_by('-recuperaciones__sum')[0]
        perdidas = Stats.objects.values('jugador_id').annotate(Sum('perdidas')).order_by('-perdidas__sum')[0]
        ptsMarca = Stats.objects.values('jugador_id').annotate(Sum('ptsMarca')).order_by('-ptsMarca__sum')[0]
        maxs = puntos|minutos|goles|asist|asistSinGol|paradas|amarillas|rojas|centros|despejes|penFallados|encajados|tiros|regates|recuperaciones|perdidas|ptsMarca
        return maxs

    #plantearse si incluir minimos solo habria que cambiar el orderby de los maximos

    def valorJornada(self):
        return Valores.objects.filter(jugador_id=self.jugador_id,jornada=self.jornada)

    def __str__(self):
        return self.jugador_id.nombre + " J" + str(self.jornada)

class Valores(models.Model):
    jugador_id = models.ForeignKey(Jugador,on_delete=models.CASCADE)
    jornada = models.SmallIntegerField()
    valor = models.FloatField()

    def getLastValor(id):
        return Valores.objects.filter(jugador_id = id).order_by("jornada").last().valor

    def __str__(self):
        #Me gustaría que la string fuese esta para poder verlo mejor en la bbdd
        #self.jugador_id.nombre + " J" + str(self.jornada)
        return str(self.valor)

class Plantilla(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    jugadores = models.ManyToManyField(Jugador,blank=True)

    def __str__(self):
        return "Plantilla de " + str(self.user.username)
    
class Favoritos(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    jugadores = models.ManyToManyField(Jugador,blank=True)

    def __str__(self):
        return "Favoritos de " + str(self.user.username)








