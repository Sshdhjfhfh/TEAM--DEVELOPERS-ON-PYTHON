from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from portal import models as portal_models

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


class DecoradorRolTests(TestCase):
    """Verifica la autorización por rol en los módulos del Tópico."""

    def crear_usuario(self, rol):
        usuario = User.objects.create_user(username=f'user_{rol.lower()}', password='clave_segura_123')
        usuario.profile.role = rol
        usuario.profile.save()
        return usuario

    def test_no_autenticado_redirige_a_login(self):
        respuesta = self.client.get(reverse('inventario:crear'))
        self.assertRedirects(
            respuesta,
            f"{reverse('accounts:login')}?next={reverse('inventario:crear')}",
        )

    def test_enfermero_no_accede_a_inventario(self):
        self.client.force_login(self.crear_usuario(Profile.Role.ENFERMERO))
        respuesta = self.client.get(reverse('inventario:crear'))
        self.assertRedirects(respuesta, reverse('dashboard'))

    def test_farmaceutico_si_accede_a_inventario(self):
        self.client.force_login(self.crear_usuario(Profile.Role.FARMACEUTICO))
        respuesta = self.client.get(reverse('inventario:crear'))
        self.assertEqual(respuesta.status_code, 200)

    def test_estudiante_no_accede_a_pacientes(self):
        usuario = self.crear_usuario(Profile.Role.ESTUDIANTE)
        portal_models.Estudiante.objects.create(
            codigo='2024777777',
            dni='33445566',
            nombres='Prueba',
            apellidos='Estudiante',
            escuela='SISTEMAS',
            ciclo=5,
            matriculado=True,
            user=usuario,
        )
        self.client.force_login(usuario)
        respuesta = self.client.get(reverse('pacientes:crear'))
        self.assertRedirects(respuesta, reverse('portal:mis_citas'))

    def test_enfermero_si_accede_a_pacientes(self):
        self.client.force_login(self.crear_usuario(Profile.Role.ENFERMERO))
        respuesta = self.client.get(reverse('pacientes:crear'))
        self.assertEqual(respuesta.status_code, 200)

    def test_admin_accede_a_todo(self):
        superusuario = User.objects.create_superuser(username='root', password='clave_segura_123')
        self.client.force_login(superusuario)
        self.assertEqual(self.client.get(reverse('inventario:crear')).status_code, 200)
        self.assertEqual(self.client.get(reverse('atenciones:crear')).status_code, 200)
