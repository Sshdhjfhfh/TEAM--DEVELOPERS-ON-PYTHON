from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Medicamento(models.Model):
    """Medicamento, insumo o equipo del almacén del Tópico."""

    class Categoria(models.TextChoices):
        MEDICAMENTO = 'MEDICAMENTO', 'Medicamento'
        INSUMO = 'INSUMO', 'Insumo'
        EQUIPO = 'EQUIPO', 'Equipo'

    nombre = models.CharField('Nombre', max_length=150)
    descripcion = models.TextField('Descripción', blank=True)
    categoria = models.CharField(
        'Categoría',
        max_length=15,
        choices=Categoria.choices,
        default=Categoria.MEDICAMENTO,
    )
    unidad = models.CharField('Unidad de medida', max_length=20, default='unidad')
    stock_actual = models.PositiveIntegerField(
        'Stock actual',
        default=0,
        validators=[MinValueValidator(0)],
    )
    stock_minimo = models.PositiveIntegerField(
        'Stock mínimo',
        default=0,
        validators=[MinValueValidator(0)],
    )
    precio_unitario = models.DecimalField(
        'Precio unitario (S/)',
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    fecha_vencimiento = models.DateField('Fecha de vencimiento', null=True, blank=True)
    proveedor = models.CharField('Proveedor', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.stock_actual} {self.unidad})'

    @property
    def stock_critico(self):
        return self.stock_actual <= self.stock_minimo


class MovimientoInventario(models.Model):
    """Movimiento de entrada, salida o ajuste de stock."""

    class Tipo(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SALIDA = 'SALIDA', 'Salida'
        AJUSTE = 'AJUSTE', 'Ajuste'

    medicamento = models.ForeignKey(
        Medicamento,
        on_delete=models.CASCADE,
        related_name='movimientos',
        verbose_name='Medicamento',
    )
    tipo = models.CharField('Tipo', max_length=10, choices=Tipo.choices)
    cantidad = models.PositiveIntegerField('Cantidad', validators=[MinValueValidator(1)])
    fecha = models.DateTimeField('Fecha', auto_now_add=True)
    motivo = models.CharField('Motivo', max_length=200, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_inventario',
        verbose_name='Usuario',
    )
    atencion = models.ForeignKey(
        'atenciones.Atencion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos',
        verbose_name='Atención asociada',
    )

    class Meta:
        verbose_name = 'Movimiento de inventario'
        verbose_name_plural = 'Movimientos de inventario'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} de {self.cantidad} — {self.medicamento.nombre}'

    @property
    def usuario_nombre(self):
        if self.usuario_id:
            return self.usuario.get_full_name() or self.usuario.username
        return '—'

    def clean(self):
        super().clean()
        if self.tipo == self.Tipo.SALIDA and self.medicamento_id:
            if self.cantidad > self.medicamento.stock_actual:
                raise ValidationError(
                    {'cantidad': 'No hay stock suficiente para realizar la salida.'}
                )

    def save(self, *args, **kwargs):
        if self.tipo == self.Tipo.SALIDA and self.medicamento_id:
            if self.cantidad > self.medicamento.stock_actual:
                raise ValidationError(
                    {'cantidad': 'No hay stock suficiente para realizar la salida.'}
                )
        super().save(*args, **kwargs)
        medicamento = self.medicamento
        if self.tipo == self.Tipo.ENTRADA:
            medicamento.stock_actual += self.cantidad
        elif self.tipo == self.Tipo.SALIDA:
            medicamento.stock_actual -= self.cantidad
        else:  # AJUSTE: fija el stock al valor indicado
            medicamento.stock_actual = self.cantidad
        medicamento.save(update_fields=['stock_actual'])
