from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser

from .models import Paciente


def crear_usuario(**kwargs):
    return CustomUser.objects.create_user(
        username=kwargs.get('username', 'test'),
        password=kwargs.get('password', 'pass12345'),
        first_name=kwargs.get('first_name', 'Test'),
        last_name=kwargs.get('last_name', 'User'),
    )


def crear_paciente(**kwargs):
    return Paciente.objects.create(
        nombres=kwargs.get('nombres', 'Ana'),
        apellidos=kwargs.get('apellidos', 'Quispe'),
        dni=kwargs.get('dni', '12345678'),
        fecha_nacimiento=kwargs.get('fecha_nacimiento', date(2001, 1, 1)),
        sexo=kwargs.get('sexo', 'F'),
        tipo_sangre=kwargs.get('tipo_sangre', 'O+'),
    )


class PacienteModelTests(TestCase):
    def test_nombre_completo(self):
        paciente = crear_paciente()
        self.assertEqual(paciente.nombre_completo, 'Ana Quispe')

    def test_edad_calculada(self):
        paciente = crear_paciente(fecha_nacimiento=date(2001, 1, 1))
        self.assertEqual(paciente.edad, 25)  # Año 2026

    def test_dni_no_numerico_invalido(self):
        with self.assertRaises(ValidationError):
            Paciente.objects.create(
                nombres='X', apellidos='Y', dni='abcdefgh',
                fecha_nacimiento=date(2000, 1, 1), sexo='M',
            )

    def test_dni_duplicado_rechazado(self):
        crear_paciente(dni='12345678')
        with self.assertRaises(Exception):
            crear_paciente(dni='12345678')


class PacienteViewTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)
        self.paciente = crear_paciente()

    def test_lista_pacientes_requiere_login(self):
        self.client.logout()
        respuesta = self.client.get(reverse('pacientes:lista'))
        self.assertEqual(respuesta.status_code, 302)

    def test_lista_pacientes(self):
        respuesta = self.client.get(reverse('pacientes:lista'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Ana Quispe')

    def test_crear_paciente(self):
        respuesta = self.client.post(reverse('pacientes:crear'), {
            'nombres': 'Luis',
            'apellidos': 'García',
            'dni': '23456789',
            'fecha_nacimiento': '1998-07-25',
            'sexo': 'M',
            'telefono': '',
            'direccion': '',
            'tipo_sangre': 'A+',
            'alergias': '',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Paciente.objects.filter(dni='23456789').exists())

    def test_detalle_paciente(self):
        respuesta = self.client.get(reverse('pacientes:detalle', args=[self.paciente.pk]))
        self.assertEqual(respuesta.status_code, 200)

    def test_busqueda_paciente_por_dni(self):
        respuesta = self.client.get(reverse('pacientes:lista'), {'q': '12345678'})
        self.assertContains(respuesta, 'Ana Quispe')
