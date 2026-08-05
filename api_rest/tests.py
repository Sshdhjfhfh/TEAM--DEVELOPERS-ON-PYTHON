from datetime import date

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from atenciones.models import Atencion
from inventario.models import Medicamento
from pacientes.models import Paciente


class ApiAuthTests(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='api', password='pass12345')
        self.token = Token.objects.create(user=self.usuario)
        self.paciente = Paciente.objects.create(
            nombres='Ana', apellidos='Quispe', dni='12345678',
            fecha_nacimiento=date(2001, 1, 1), sexo='F', tipo_sangre='O+',
        )

    def test_obtener_token(self):
        respuesta = self.client.post(reverse('api:api-token'), {
            'username': 'api', 'password': 'pass12345',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('token', respuesta.data)

    def test_pacientes_requiere_autenticacion(self):
        respuesta = self.client.get(reverse('api:paciente-list'))
        self.assertEqual(respuesta.status_code, 401)

    def test_listar_pacientes_autenticado(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        respuesta = self.client.get(reverse('api:paciente-list'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['count'], 1)

    def test_crear_paciente_por_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        respuesta = self.client.post(reverse('api:paciente-list'), {
            'nombres': 'Luis',
            'apellidos': 'García',
            'dni': '23456789',
            'fecha_nacimiento': '1998-07-25',
            'sexo': 'M',
            'tipo_sangre': 'A+',
        })
        self.assertEqual(respuesta.status_code, 201)

    def test_crear_atencion_por_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        respuesta = self.client.post(reverse('api:atencion-list'), {
            'paciente': self.paciente.pk,
            'motivo_consulta': 'Dolor abdominal',
            'nivel_triage': 'ROJO',
            'estado': 'EN_ESPERA',
        })
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Atencion.objects.count(), 1)

    def test_filtrar_medicamentos_criticos(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        Medicamento.objects.create(nombre='A', stock_actual=2, stock_minimo=5)
        Medicamento.objects.create(nombre='B', stock_actual=50, stock_minimo=5)
        respuesta = self.client.get(reverse('api:medicamento-list'), {'criticos': 'true'})
        self.assertEqual(respuesta.data['count'], 1)
        self.assertEqual(respuesta.data['results'][0]['nombre'], 'A')

    def test_movimiento_asigna_usuario_automaticamente(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        med = Medicamento.objects.create(nombre='C', stock_actual=10, stock_minimo=5)
        respuesta = self.client.post(reverse('api:movimiento-list'), {
            'medicamento': med.pk,
            'tipo': 'ENTRADA',
            'cantidad': 5,
            'motivo': 'Compra',
        })
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data['usuario'], self.usuario.pk)
