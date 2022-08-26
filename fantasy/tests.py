from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.


class listadoTestCase(TestCase):
    def setUp(self):
        self.user=User(id=0,username="javier")
        self.user.set_password('1234')

        