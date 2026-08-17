from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from pacientes.models import Paciente


class ReportesViewTests(TestCase):
    def setUp(self):
        self.usuario = CustomUser.objects.create_user(username='test', password='pass12345')
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


class ReportesExportacionTests(TestCase):
    def setUp(self):
        self.usuario = CustomUser.objects.create_user(username='test', password='pass12345')
        self.client.force_login(self.usuario)
        Paciente.objects.create(
            nombres='Ana',
            apellidos='Quispe',
            dni='12345678',
            fecha_nacimiento='2000-01-15',
            sexo='F',
            registrado_por=self.usuario,
        )

    def test_exportar_pacientes_csv(self):
        respuesta = self.client.get(reverse('reportes:pacientes_csv'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment', respuesta['Content-Disposition'])
        self.assertIn('12345678', respuesta.content.decode('utf-8'))

    def test_exportar_atenciones_csv(self):
        respuesta = self.client.get(reverse('reportes:atenciones_csv'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'text/csv; charset=utf-8')

    def test_exportar_inventario_csv(self):
        respuesta = self.client.get(reverse('reportes:inventario_csv'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'text/csv; charset=utf-8')

    def test_imprimir_pacientes(self):
        respuesta = self.client.get(reverse('reportes:pacientes_imprimir'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Quispe')

    def test_imprimir_atenciones(self):
        respuesta = self.client.get(reverse('reportes:atenciones_imprimir'))
        self.assertEqual(respuesta.status_code, 200)

    def test_imprimir_inventario(self):
        respuesta = self.client.get(reverse('reportes:inventario_imprimir'))
        self.assertEqual(respuesta.status_code, 200)

    def test_exportaciones_requieren_login(self):
        self.client.logout()
        for ruta in [
            'reportes:pacientes_csv',
            'reportes:atenciones_csv',
            'reportes:inventario_csv',
            'reportes:pacientes_imprimir',
            'reportes:atenciones_imprimir',
            'reportes:inventario_imprimir',
        ]:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(reverse(ruta)).status_code, 302)
