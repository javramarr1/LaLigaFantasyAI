from django.test import TestCase
from django.contrib.auth.models import User

from django.contrib import auth

from .scraping import leer_jugadores, estadisticas_bbdd

import pandas as pd
from joblib import dump
from sklearn.neighbors import NearestNeighbors
from django.db.models import Sum,Count
from .models import Equipo, Jugador,Stats,Valores, Plantilla, Favoritos

# Create your tests here.


class ListadoTestCase(TestCase):
    def setUp(self):
        self.user=User(id=0,username="javier")
        self.user.set_password('1234')

        self.user.save()

        leer_jugadores('fantasy/csv/listado2122.csv')
        estadisticas_bbdd('fantasy/csv/porteros2122.csv',False,1)
        estadisticas_bbdd('fantasy/csv/defensas2122.csv',False,1)
        estadisticas_bbdd('fantasy/csv/medios2122.csv',False,1)
        estadisticas_bbdd('fantasy/csv/delanteros2122.csv',False,1)
        jugadores = Jugador.objects.all()

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

    def test_jugadores(self):
        c = self.client
        response = c.get('/')
        self.assertTrue(len(response.context['jugadores'])==486)
        self.assertTrue(len(response.context['page_obj'])==25)
        response = c.get('/?page=20')
        self.assertTrue(len(response.context['page_obj'])==11)
        response = c.get('/club/5')
        self.assertTrue(response.context['equipo'].nombre.strip()=="Real Betis".strip())
        self.assertTrue(len(response.context['club'])!=0)
        response = c.get('/perfil/250')
        self.assertTrue(response.context['jugador'].nombre.strip()=="Benzema")
        self.assertTrue(len(response.context['totales'])>10)
        #algoritmo de jugadores similares
        self.assertTrue(len(response.context['s2'])==5)
        #algoritmo de prediccion de valores de mercado
        self.assertTrue(response.context['v1j']!="")
        self.assertTrue(response.context['v5j']!="")
        self.assertTrue(response.context['v10j']!="")


class LoginTestCase(TestCase):
    def setUp(self):
        self.user=User(id=0,username="javier")
        self.user.set_password('1234')

        self.user.save()

    def test_login_positive(self):
        response = self.client.post('/login/', {'username': 'javier', 'password': '1234'})
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertRedirects(response, '/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)

    def test_login_negative(self):
        self.client.post('/login/', {'username': 'usuario', 'password': 'qwery'})
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_logout_positive(self):
        c = self.client
        c.post('/login/', {'username': 'javier', 'password': '1234'})
        response = c.get('/logout/')
        user = auth.get_user(c)
        self.assertTrue(response.status_code == 302)
        self.assertFalse(user.is_authenticated)

class RegistroTestCase(TestCase):

    def setUp(self):
        self.data = {'username': 'javier','correo': 'hola@example.com', 'password': 'Contrasena22@', 'password2': 'Contrasena22@'} 

    def test_registro_positive(self):
        response = self.client.post('/registro/', self.data)
        self.assertRedirects(response, '/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)

    def test_username_already_exists(self):
        response = self.client.post('/registro/', self.data)
        self.assertRedirects(response, '/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)
        self.data['correo'] = 'hola2@example.com'
        self.client.post('/registro/', self.data)
        self.assertTrue(User.objects.all().count()==1)

    def test_correo_already_exists(self):
        
        response = self.client.post('/registro/', self.data)
        self.assertRedirects(response, '/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)
        self.data['username'] = 'javier2'
        self.client.post('/registro/', self.data)
        self.assertTrue(User.objects.all().count()==1)

    def test_different_password(self):
        self.data['password'] = "Contrasena22@"
        self.data['password2'] = "Contrasena21@"
        response = self.client.post('/registro/', self.data)
        num_usuarios = User.objects.all().count()
        self.assertTrue(num_usuarios == 0)
        error = response.context['form'].errors['password2'][0]
        self.assertTrue(error == "Las contraseñas no coinciden")

    def test_wrong_password(self):
        self.data['password'] = "123"
        response = self.client.post('/registro/', self.data)
        num_usuarios = User.objects.all().count()
        self.assertTrue(num_usuarios == 0)
        error = response.context['form'].errors['password'][0]
        self.assertTrue(error == 'Al menos 8 caracteres, un dígito, una minúscula y una mayúscula.')

    def test_wrong_correo(self):
        self.data['correo'] = "hola.es"
        response = self.client.post('/registro/', self.data)
        num_usuarios = User.objects.all().count()
        self.assertTrue(num_usuarios == 0)
        error = response.context['form'].errors['correo'][0]
        self.assertTrue(error == 'Inserta un correo electrónico válido')

    def test_wrong_username(self):
        self.data['username'] = "hola"
        response = self.client.post('/registro/', self.data)
        num_usuarios = User.objects.all().count()
        self.assertTrue(num_usuarios == 0)
        error = response.context['form'].errors['username'][0]
        self.assertTrue(error == 'El nombre de usuario debe tener una longitud mínima de 5 caracteres')

