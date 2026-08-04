from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from pacientes.models import Paciente

from .models import Cita, Estudiante


def _proximo_dia_habil():
    fecha = timezone.localdate() + timedelta(days=1)
    while fecha.weekday() >= 5:
        fecha += timedelta(days=1)
    return fecha


def _crear_estudiante(codigo='2024999999', dni='87654321', matriculado=True):
    return Estudiante.objects.create(
        codigo=codigo,
        dni=dni,
        nombres='Prueba',
        apellidos='Estudiante Test',
        escuela=Estudiante.Escuela.SISTEMAS,
        ciclo=5,
        matriculado=matriculado,
    )


def _crear_cuenta_estudiante(codigo='2024999999', dni='87654321'):
    estudiante = _crear_estudiante(codigo, dni)
    user = User.objects.create_user(username=codigo, password='clave_segura_123')
    user.profile.role = Profile.Role.ESTUDIANTE
    user.profile.save()
    estudiante.user = user
    estudiante.save(update_fields=['user'])
    return estudiante, user


def _crear_personal():
    user = User.objects.create_user(username='medico_test', password='clave_segura_123')
    user.profile.role = Profile.Role.MEDICO
    user.profile.save()
    return user


class EstudianteModelTests(TestCase):
    def test_nombre_completo_y_tiene_cuenta(self):
        estudiante = _crear_estudiante()
        self.assertEqual(estudiante.nombre_completo, 'Prueba Estudiante Test')
        self.assertFalse(estudiante.tiene_cuenta)
        self.assertIn('2024999999', str(estudiante))

    def test_tiene_cuenta_despues_de_vincular(self):
        estudiante, _ = _crear_cuenta_estudiante()
        self.assertTrue(estudiante.tiene_cuenta)


class CitaModelTests(TestCase):
    def test_slots_del_dia(self):
        # 08:00-12:30 (9 slots) + 14:00-16:30 (5 slots) = 14 slots de 30 min
        self.assertEqual(len(Cita.slots_del_dia()), 14)

    def test_slots_disponibles_excluye_ocupados(self):
        estudiante = _crear_estudiante()
        fecha = _proximo_dia_habil()
        Cita.objects.create(
            estudiante=estudiante,
            fecha=fecha,
            hora=Cita.slots_del_dia()[0],
            motivo='Control',
        )
        disponibles = Cita.slots_disponibles(fecha)
        self.assertEqual(len(disponibles), 13)
        self.assertNotIn(Cita.slots_del_dia()[0], disponibles)

    def test_clean_rechaza_sabado(self):
        sabado = timezone.localdate()
        while sabado.weekday() != 5:
            sabado += timedelta(days=1)
        cita = Cita(
            estudiante=_crear_estudiante(),
            fecha=sabado,
            hora=Cita.slots_del_dia()[0],
            motivo='Prueba',
        )
        with self.assertRaises(ValidationError):
            cita.full_clean()

    def test_activa(self):
        cita = Cita(
            estudiante=_crear_estudiante(),
            fecha=_proximo_dia_habil(),
            hora=Cita.slots_del_dia()[0],
            motivo='Prueba',
            estado=Cita.Estado.PENDIENTE,
        )
        self.assertTrue(cita.activa)


class RegistroPortalTests(TestCase):
    def test_validar_codigo_get(self):
        respuesta = self.client.get(reverse('portal:validar_codigo'))
        self.assertEqual(respuesta.status_code, 200)

    def test_validar_codigo_codigo_inexistente(self):
        respuesta = self.client.post(reverse('portal:validar_codigo'), {
            'codigo': '2024999999',
            'dni': '87654321',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'no figura en el padrón')

    def test_validar_codigo_dni_no_coincide(self):
        _crear_estudiante()
        respuesta = self.client.post(reverse('portal:validar_codigo'), {
            'codigo': '2024999999',
            'dni': '11111111',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'no coincide')

    def test_validar_codigo_sin_matricula(self):
        _crear_estudiante(matriculado=False)
        respuesta = self.client.post(reverse('portal:validar_codigo'), {
            'codigo': '2024999999',
            'dni': '87654321',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'matrícula activa')

    def test_validar_codigo_con_cuenta_existente(self):
        _crear_cuenta_estudiante()
        respuesta = self.client.post(reverse('portal:validar_codigo'), {
            'codigo': '2024999999',
            'dni': '87654321',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'ya tiene una cuenta')

    def test_flujo_completo_registro(self):
        _crear_estudiante()
        respuesta = self.client.post(reverse('portal:validar_codigo'), {
            'codigo': '2024999999',
            'dni': '87654321',
        })
        self.assertRedirects(respuesta, reverse('portal:completar_registro'))

        respuesta = self.client.post(reverse('portal:completar_registro'), {
            'fecha_nacimiento': '2002-05-10',
            'sexo': 'M',
            'telefono': '999888777',
            'password1': 'clave_segura_123',
            'password2': 'clave_segura_123',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(User.objects.filter(username='2024999999').exists())
        estudiante = Estudiante.objects.get(codigo='2024999999')
        self.assertTrue(estudiante.tiene_cuenta)
        self.assertIsNotNone(estudiante.paciente)
        self.assertEqual(estudiante.user.profile.role, Profile.Role.ESTUDIANTE)
        self.assertEqual(Paciente.objects.get(dni='87654321').nombres, 'Prueba')

    def test_completar_registro_sin_sesion_redirige(self):
        respuesta = self.client.get(reverse('portal:completar_registro'))
        self.assertRedirects(respuesta, reverse('portal:validar_codigo'))


class CitasEstudianteTests(TestCase):
    def setUp(self):
        self.estudiante, self.usuario = _crear_cuenta_estudiante()
        self.client.force_login(self.usuario)

    def test_reservar_cita_crea_cita(self):
        respuesta = self.client.post(reverse('portal:reservar_cita'), {
            'fecha': _proximo_dia_habil().isoformat(),
            'hora': '09:00',
            'motivo': 'Dolor de cabeza',
        })
        self.assertRedirects(respuesta, reverse('portal:mis_citas'))
        self.assertTrue(self.estudiante.citas.filter(motivo='Dolor de cabeza').exists())

    def test_no_permite_dos_citas_activas(self):
        Cita.objects.create(
            estudiante=self.estudiante,
            fecha=_proximo_dia_habil(),
            hora=Cita.slots_del_dia()[0],
            motivo='Primera',
        )
        respuesta = self.client.post(reverse('portal:reservar_cita'), {
            'fecha': _proximo_dia_habil().isoformat(),
            'hora': '09:30',
            'motivo': 'Segunda',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'cita activa')

    def test_no_permite_slot_ocupado(self):
        otro, _ = _crear_cuenta_estudiante(codigo='2024888888', dni='11223344')
        Cita.objects.create(
            estudiante=otro,
            fecha=_proximo_dia_habil(),
            hora=Cita.slots_del_dia()[0],
            motivo='Ocupado',
        )
        respuesta = self.client.post(reverse('portal:reservar_cita'), {
            'fecha': _proximo_dia_habil().isoformat(),
            'hora': Cita.slots_del_dia()[0].strftime('%H:%M'),
            'motivo': 'Intento',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(self.estudiante.citas.filter(motivo='Intento').exists())

    def test_cancelar_cita(self):
        cita = Cita.objects.create(
            estudiante=self.estudiante,
            fecha=_proximo_dia_habil(),
            hora=Cita.slots_del_dia()[0],
            motivo='Control',
        )
        respuesta = self.client.post(reverse('portal:cancelar_cita', args=[cita.pk]))
        self.assertRedirects(respuesta, reverse('portal:mis_citas'))
        cita.refresh_from_db()
        self.assertEqual(cita.estado, Cita.Estado.CANCELADA)

    def test_mis_citas_solo_propias(self):
        otro, _ = _crear_cuenta_estudiante(codigo='2024888888', dni='11223344')
        Cita.objects.create(
            estudiante=otro,
            fecha=_proximo_dia_habil(),
            hora=Cita.slots_del_dia()[0],
            motivo='De otro',
        )
        Cita.objects.create(
            estudiante=self.estudiante,
            fecha=_proximo_dia_habil(),
            hora=Cita.slots_del_dia()[1],
            motivo='Mía',
        )
        respuesta = self.client.get(reverse('portal:mis_citas'))
        self.assertEqual(respuesta.status_code, 200)
        citas = list(respuesta.context['citas'])
        self.assertEqual(len(citas), 1)
        self.assertEqual(citas[0].motivo, 'Mía')


class AgendaPersonalTests(TestCase):
    def setUp(self):
        self.estudiante, _ = _crear_cuenta_estudiante()

    def test_estudiante_no_accede_a_agenda(self):
        self.client.force_login(self.estudiante.user)
        respuesta = self.client.get(reverse('portal:lista_citas'))
        self.assertRedirects(respuesta, reverse('portal:mis_citas'))

    def test_convertir_cita_en_atencion(self):
        personal = _crear_personal()
        paciente = Paciente.objects.create(
            nombres='Prueba',
            apellidos='Estudiante Test',
            dni=self.estudiante.dni,
            fecha_nacimiento='2002-05-10',
            sexo='M',
            registrado_por=personal,
        )
        self.estudiante.paciente = paciente
        self.estudiante.save(update_fields=['paciente'])
        cita = Cita.objects.create(
            estudiante=self.estudiante,
            fecha=_proximo_dia_habil(),
            hora=Cita.slots_del_dia()[0],
            motivo='Control rutinario',
            estado=Cita.Estado.CONFIRMADA,
        )
        self.client.force_login(personal)
        respuesta = self.client.post(reverse('portal:convertir_cita', args=[cita.pk]))
        self.assertEqual(respuesta.status_code, 302)
        cita.refresh_from_db()
        self.assertEqual(cita.estado, Cita.Estado.ATENDIDA)
        self.assertIsNotNone(cita.atencion)
        atencion = cita.atencion
        self.assertEqual(atencion.paciente, paciente)
        self.assertEqual(atencion.motivo_consulta, 'Control rutinario')
