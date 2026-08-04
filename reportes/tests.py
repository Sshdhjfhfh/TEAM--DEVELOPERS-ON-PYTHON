from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ReportesViewTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='test', password='pass12345')
        self.client.force_login(self.usuario)

    def test_dashboard(self):
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 200)

    def test_dashboard_requiere_login(self):
        self.client.logout()
        respuesta = self.client.get(reverse('dashboard'))
        self.assertEqual(respuesta.status_code, 302)

    def test_reporte_pacientes(self):
        respuesta = self.client.get(reverse('reportes:pacientes'))
        self.assertEqual(respuesta.status_code, 200)

    def test_reporte_atenciones(self):
        respuesta = self.client.get(reverse('reportes:atenciones'))
        self.assertEqual(respuesta.status_code, 200)

    def test_reporte_inventario(self):
        respuesta = self.client.get(reverse('reportes:inventario'))
        self.assertEqual(respuesta.status_code, 200)
