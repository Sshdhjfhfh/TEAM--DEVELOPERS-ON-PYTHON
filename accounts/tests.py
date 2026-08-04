from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class ProfileModelTests(TestCase):
    def test_perfil_se_crea_automaticamente(self):
        usuario = User.objects.create_user(username='test', password='pass12345')
        self.assertTrue(Profile.objects.filter(user=usuario).exists())
        self.assertEqual(usuario.profile.role, Profile.Role.ENFERMERO)

    def test_str_perfil(self):
        usuario = User.objects.create_user(
            username='test', password='pass12345',
            first_name='Ana', last_name='Quispe',
        )
        self.assertEqual(str(usuario.profile), 'Ana Quispe (Enfermero(a))')


class RegistroViewTests(TestCase):
    def test_registro_crea_usuario(self):
        respuesta = self.client.post(reverse('accounts:registro'), {
            'username': 'nuevo',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'email': 'nuevo@test.com',
            'password1': 'clave_segura_123',
            'password2': 'clave_segura_123',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(User.objects.filter(username='nuevo').exists())
        self.assertTrue(Profile.objects.filter(user__username='nuevo').exists())

    def test_login_vista_redirige_al_dashboard(self):
        User.objects.create_user(username='test', password='pass12345')
        self.assertTrue(self.client.login(username='test', password='pass12345'))
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 200)
