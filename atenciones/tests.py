from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from inventario.models import Medicamento, MovimientoInventario
from pacientes.models import Paciente

from .models import Atencion, RecetaMedicamento, SignosVitales


def crear_contexto():
    usuario = CustomUser.objects.create_user(username='test', password='pass12345')
    paciente = Paciente.objects.create(
        nombres='Ana', apellidos='Quispe', dni='12345678',
        fecha_nacimiento=date(2001, 1, 1), sexo='F', tipo_sangre='O+',
    )
    return usuario, paciente


class AtencionModelTests(TestCase):
    def setUp(self):
        self.usuario, self.paciente = crear_contexto()

    def test_crear_atencion_y_signos(self):
        atencion = Atencion.objects.create(
            paciente=self.paciente,
            medico=self.usuario,
            motivo_consulta='Dolor abdominal',
            nivel_triage=Atencion.NivelTriage.ROJO,
            estado=Atencion.Estado.EN_ATENCION,
        )
        signos = SignosVitales.objects.create(
            atencion=atencion,
            temperatura=38.5,
            presion_sistolica=120,
            presion_diastolica=80,
        )
        self.assertEqual(signos.presion_arterial, '120/80')
        self.assertTrue(atencion.tiene_signos_vitales)

    def test_estado_default_en_espera(self):
        atencion = Atencion.objects.create(paciente=self.paciente, motivo_consulta='Chequeo')
        self.assertEqual(atencion.estado, Atencion.Estado.EN_ESPERA)


class AtencionViewTests(TestCase):
    def setUp(self):
        self.usuario, self.paciente = crear_contexto()
        self.client.force_login(self.usuario)
        self.atencion = Atencion.objects.create(
            paciente=self.paciente, motivo_consulta='Dolor de cabeza',
        )

    def test_lista_atenciones(self):
        respuesta = self.client.get(reverse('atenciones:lista'))
        self.assertEqual(respuesta.status_code, 200)

    def test_crear_atencion(self):
        respuesta = self.client.post(reverse('atenciones:crear'), {
            'paciente': self.paciente.pk,
            'medico': self.usuario.pk,
            'motivo_consulta': 'Fiebre',
            'anamnesis': '',
            'diagnostico': '',
            'tratamiento': '',
            'observaciones': '',
            'nivel_triage': 'AMARILLO',
            'estado': 'EN_ESPERA',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Atencion.objects.filter(motivo_consulta='Fiebre').exists())

    def test_cola_atenciones(self):
        respuesta = self.client.get(reverse('atenciones:cola'))
        self.assertEqual(respuesta.status_code, 200)

    def test_registrar_signos(self):
        url = reverse('atenciones:signos', args=[self.atencion.pk])
        respuesta = self.client.post(url, {
            'temperatura': '37.5',
            'presion_sistolica': 110,
            'presion_diastolica': 70,
            'pulso': 80,
            'frecuencia_respiratoria': 16,
            'saturacion_oxigeno': 98,
            'peso': 60,
            'talla': 160,
        })
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(SignosVitales.objects.filter(atencion=self.atencion).exists())


class RecetaMedicamentoTests(TestCase):
    def setUp(self):
        self.usuario, self.paciente = crear_contexto()
        self.client.force_login(self.usuario)
        self.atencion = Atencion.objects.create(
            paciente=self.paciente, motivo_consulta='Dolor de cabeza',
        )
        self.medicamento = Medicamento.objects.create(
            nombre='Paracetamol 500mg', stock_actual=20, stock_minimo=5,
        )

    def test_receta_descuenta_stock(self):
        item = RecetaMedicamento.objects.create(
            atencion=self.atencion,
            medicamento=self.medicamento,
            cantidad=6,
            indicaciones='1 cada 8 horas por 2 días',
        )
        self.assertEqual(item.medicamento.stock_actual, 14)
        movimiento = MovimientoInventario.objects.get(medicamento=self.medicamento)
        self.assertEqual(movimiento.tipo, MovimientoInventario.Tipo.SALIDA)
        self.assertEqual(movimiento.cantidad, 6)
        self.assertEqual(movimiento.atencion, self.atencion)
        self.assertIn('Receta', movimiento.motivo)

    def test_receta_sin_stock_suficiente_rechazada(self):
        with self.assertRaises(ValidationError):
            RecetaMedicamento.objects.create(
                atencion=self.atencion,
                medicamento=self.medicamento,
                cantidad=25,
            )

    def test_vista_agregar_receta(self):
        respuesta = self.client.post(
            reverse('atenciones:agregar_receta', args=[self.atencion.pk]),
            {'medicamento': self.medicamento.pk, 'cantidad': 4, 'indicaciones': '1 cada 8 horas'},
        )
        self.assertEqual(respuesta.status_code, 302)
        self.medicamento.refresh_from_db()
        self.assertEqual(self.medicamento.stock_actual, 16)
        self.assertTrue(
            RecetaMedicamento.objects.filter(atencion=self.atencion).exists()
        )

    def test_vista_agregar_receta_sin_stock(self):
        self.medicamento.stock_actual = 2
        self.medicamento.save()
        respuesta = self.client.post(
            reverse('atenciones:agregar_receta', args=[self.atencion.pk]),
            {'medicamento': self.medicamento.pk, 'cantidad': 5},
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(self.medicamento.stock_actual, 2)
