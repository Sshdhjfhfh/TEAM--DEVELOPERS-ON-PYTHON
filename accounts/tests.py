from django.test import TestCase
from django.urls import reverse

from portal import models as portal_models

from .models import CustomUser


class CustomUserModelTests(TestCase):
    def test_usuario_creado_con_rol_por_defecto(self):
        usuario = CustomUser.objects.create_user(username='test', password='pass12345')
        self.assertEqual(usuario.role, CustomUser.Role.ENFERMERO)

    def test_str_usuario(self):
        usuario = CustomUser.objects.create_user(
            username='test', password='pass12345',
            first_name='Ana', last_name='Quispe',
        )
        self.assertEqual(str(usuario), 'Ana Quispe (Enfermero(a))')

    def test_es_estudiante_y_es_personal(self):
        estudiante = CustomUser.objects.create_user(username='est', password='pass12345')
        estudiante.role = CustomUser.Role.ESTUDIANTE
        self.assertTrue(estudiante.es_estudiante)
        self.assertFalse(estudiante.es_personal)


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
        self.assertTrue(CustomUser.objects.filter(username='nuevo').exists())

    def test_login_vista_redirige_al_dashboard(self):
        CustomUser.objects.create_user(username='test', password='pass12345')
        self.assertTrue(self.client.login(username='test', password='pass12345'))
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 200)


class DecoradorRolTests(TestCase):
    """Verifica la autorización por rol en los módulos del Tópico."""

    def crear_usuario(self, rol):
        usuario = CustomUser.objects.create_user(
            username=f'user_{rol.lower()}', password='clave_segura_123',
        )
        usuario.role = rol
        usuario.save(update_fields=['role'])
        return usuario

    def test_no_autenticado_redirige_a_login(self):
        respuesta = self.client.get(reverse('inventario:crear'))
        self.assertRedirects(
            respuesta,
            f"{reverse('accounts:login')}?next={reverse('inventario:crear')}",
        )

    def test_enfermero_no_accede_a_inventario(self):
        self.client.force_login(self.crear_usuario(CustomUser.Role.ENFERMERO))
        respuesta = self.client.get(reverse('inventario:crear'))
        self.assertRedirects(respuesta, reverse('dashboard'))

    def test_farmaceutico_si_accede_a_inventario(self):
        self.client.force_login(self.crear_usuario(CustomUser.Role.FARMACEUTICO))
        respuesta = self.client.get(reverse('inventario:crear'))
        self.assertEqual(respuesta.status_code, 200)

    def test_estudiante_no_accede_a_pacientes(self):
        usuario = self.crear_usuario(CustomUser.Role.ESTUDIANTE)
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
        self.client.force_login(self.crear_usuario(CustomUser.Role.ENFERMERO))
        respuesta = self.client.get(reverse('pacientes:crear'))
        self.assertEqual(respuesta.status_code, 200)

    def test_admin_accede_a_todo(self):
        superusuario = CustomUser.objects.create_superuser(username='root', password='clave_segura_123')
        self.client.force_login(superusuario)
        self.assertEqual(self.client.get(reverse('inventario:crear')).status_code, 200)
        self.assertEqual(self.client.get(reverse('atenciones:crear')).status_code, 200)


class GestionUsuariosWebTests(TestCase):
    """CRUD de usuarios desde la web con create_user() (requisito Sprint 3)."""

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(username='admin', password='clave_segura_123')
        self.client.force_login(self.admin)

    def test_lista_usuarios(self):
        respuesta = self.client.get(reverse('accounts:lista_usuarios'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'admin')

    def test_crear_usuario_con_create_user(self):
        respuesta = self.client.post(reverse('accounts:crear_usuario'), {
            'username': 'nuevo_medico',
            'first_name': 'Nuevo',
            'last_name': 'Médico',
            'email': 'nuevo@test.com',
            'password': 'clave_segura_123',
            'role': 'MEDICO',
            'colegiatura': 'CMP-999',
            'telefono': '999888777',
            'is_active': 'on',
        })
        self.assertRedirects(respuesta, reverse('accounts:lista_usuarios'))
        usuario = CustomUser.objects.get(username='nuevo_medico')
        self.assertEqual(usuario.role, CustomUser.Role.MEDICO)
        self.assertTrue(usuario.check_password('clave_segura_123'))

    def test_crear_usuario_sin_password_falla(self):
        respuesta = self.client.post(reverse('accounts:crear_usuario'), {
            'username': 'sinpass',
            'password': '',
            'role': 'MEDICO',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(username='sinpass').exists())

    def test_retirar_usuario_cambia_estado(self):
        usuario = CustomUser.objects.create_user(username='baja', password='pass12345')
        self.client.post(reverse('accounts:retirar_usuario', args=[usuario.pk]))
        usuario.refresh_from_db()
        self.assertFalse(usuario.is_active)
        self.assertTrue(CustomUser.objects.filter(username='baja').exists())

    def test_retirar_no_permite_desactivar_propia_cuenta(self):
        respuesta = self.client.post(reverse('accounts:retirar_usuario', args=[self.admin.pk]))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)