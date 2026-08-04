from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Medicamento, MovimientoInventario


class InventarioModelTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='test', password='pass12345')

    def crear_medicamento(self, stock=10, minimo=5):
        return Medicamento.objects.create(
            nombre='Paracetamol 500mg',
            stock_actual=stock,
            stock_minimo=minimo,
            unidad='tableta',
        )

    def test_stock_critico(self):
        self.assertTrue(self.crear_medicamento(stock=4).stock_critico)
        self.assertFalse(self.crear_medicamento(stock=50).stock_critico)

    def test_entrada_incrementa_stock(self):
        med = self.crear_medicamento(stock=10)
        MovimientoInventario.objects.create(
            medicamento=med, tipo=MovimientoInventario.Tipo.ENTRADA, cantidad=5,
            usuario=self.usuario, motivo='Compra',
        )
        med.refresh_from_db()
        self.assertEqual(med.stock_actual, 15)

    def test_salida_decrementa_stock(self):
        med = self.crear_medicamento(stock=10)
        MovimientoInventario.objects.create(
            medicamento=med, tipo=MovimientoInventario.Tipo.SALIDA, cantidad=3,
            usuario=self.usuario, motivo='Uso en atención',
        )
        med.refresh_from_db()
        self.assertEqual(med.stock_actual, 7)

    def test_salida_sin_stock_suficiente_invalida(self):
        med = self.crear_medicamento(stock=2)
        with self.assertRaises(ValidationError):
            MovimientoInventario.objects.create(
                medicamento=med, tipo=MovimientoInventario.Tipo.SALIDA, cantidad=5,
            )

    def test_ajuste_fija_stock(self):
        med = self.crear_medicamento(stock=10)
        MovimientoInventario.objects.create(
            medicamento=med, tipo=MovimientoInventario.Tipo.AJUSTE, cantidad=20,
            usuario=self.usuario, motivo='Inventario físico',
        )
        med.refresh_from_db()
        self.assertEqual(med.stock_actual, 20)


class InventarioViewTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='test', password='pass12345')
        self.client.force_login(self.usuario)
        self.med = Medicamento.objects.create(
            nombre='Ibuprofeno 400mg', stock_actual=50, stock_minimo=10,
        )

    def test_lista_medicamentos(self):
        respuesta = self.client.get(reverse('inventario:lista'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Ibuprofeno 400mg')

    def test_registrar_movimiento(self):
        respuesta = self.client.post(reverse('inventario:registrar_movimiento'), {
            'medicamento': self.med.pk,
            'tipo': 'ENTRADA',
            'cantidad': 10,
            'motivo': 'Compra',
            'atencion': '',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.med.refresh_from_db()
        self.assertEqual(self.med.stock_actual, 60)
