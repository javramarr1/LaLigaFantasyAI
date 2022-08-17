from django import forms
from django.contrib.auth.models import User
import re


class RegisterForm(forms.Form):
    username = forms.CharField(required=False, max_length=100,
                               widget=forms.TextInput(attrs={'placeholder': 'Usuario','class': 'form-control form-control-user'}),)
    correo = forms.EmailField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico','class': 'form-control form-control-user'}),error_messages={'invalid': 'Inserta un correo electrónico válido'})
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña','class': 'form-control form-control-user'}))
    password2 = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Repita la contraseña','class': 'form-control form-control-user'}))

    

    def clean_username(self):

        username = self.cleaned_data.get('username')

        if len(username) < 5:
            raise forms.ValidationError('El nombre de usuario debe tener una longitud mínima de 5 caracteres')

        if len(username) > 100:
            raise forms.ValidationError('El nombre de usuario debe tener una longitud máxima de 100 caracteres')

        user_exists = User.objects.filter(username=username).exists()

        if(user_exists):
            raise forms.ValidationError('El nombre de usuario ya existe.')

        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        regex = re.compile("^(?=\w*\d)(?=\w*[A-Z])(?=\w*[a-z])\S{8,}$")
        if not re.fullmatch(regex, password):
            raise forms.ValidationError('Al menos 8 caracteres, un dígito, una minúscula y una mayúscula.')
        return password

    def clean_password2(self):

        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError('Por favor, confirma tu contraseña')
        if password != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return password2

    def clean_correo(self):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        correo = self.cleaned_data.get('correo')
        if len(correo) < 1:
            raise forms.ValidationError('El correo no debe ser nulo')
    
        if not re.fullmatch(regex, correo):
            raise forms.ValidationError('Inserte un correo electrónico válido')

        existe_email = User.objects.filter(email=correo).exists()

        if existe_email:
            raise forms.ValidationError('La dirección de correo electrónico ya está en uso')

        return correo


class addJugadorForm(forms.Form):

    addSquad = forms.CharField(required=False)
    addFavs = forms.CharField(required=False)

class accionesJugadorForm(forms.Form):

    icon = forms.CharField(required=False)
    jug = forms.CharField(required=False)
    tipo = forms.CharField(required=False)