from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.core.exceptions import ValidationError


class Atencion(models.Model):
    """Atención médica registrada en el Tópico UNH."""

    class NivelTriage(models.TextChoices):
        ROJO = 'ROJO', 'Rojo — Emergencia'
        NARANJA = 'NARANJA', 'Naranja — Urgente'
        AMARILLO = 'AMARILLO', 'Amarillo — Prioridad media'
        VERDE = 'VERDE', 'Verde — Prioridad baja'
        AZUL = 'AZUL', 'Azul — No urgente'

    class Estado(models.TextChoices):
        EN_ESPERA = 'EN_ESPERA', 'En espera'
        EN_ATENCION = 'EN_ATENCION', 'En atención'
        ATENDIDO = 'ATENDIDO', 'Atendido'
        DERIVADO = 'DERIVADO', 'Derivado'

    paciente = models.ForeignKey(
        'pacientes.Paciente',
        on_delete=models.CASCADE,
        related_name='atenciones',
        verbose_name='Paciente',
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atenciones_realizadas',
        verbose_name='Médico / personal de salud',
    )
    fecha_atencion = models.DateTimeField('Fecha de atención', auto_now_add=True)
    motivo_consulta = models.TextField('Motivo de consulta')
    anamnesis = models.TextField('Anamnesis', blank=True)
    diagnostico = models.TextField('Diagnóstico', blank=True)
    tratamiento = models.TextField('Tratamiento / indicaciones', blank=True)
    observaciones = models.TextField('Observaciones', blank=True)
    nivel_triage = models.CharField(
        'Nivel de triage',
        max_length=10,
        choices=NivelTriage.choices,
        default=NivelTriage.AMARILLO,
    )
    estado = models.CharField(
        'Estado',
        max_length=12,
        choices=Estado.choices,
        default=Estado.EN_ESPERA,
    )

    class Meta:
        verbose_name = 'Atención'
        verbose_name_plural = 'Atenciones'
        ordering = ['-fecha_atencion']

    def __str__(self):
        return f'Atención #{self.pk} — {self.paciente} ({self.fecha_atencion:%d/%m/%Y %H:%M})'

    @property
    def tiene_signos_vitales(self):
        return hasattr(self, 'signos_vitales')

    @property
    def medico_nombre(self):
        if self.medico_id:
            return self.medico.get_full_name() or self.medico.username
        return '—'


class RecetaMedicamento(models.Model):
    """Ítem de receta médica que descuenta automáticamente el inventario."""

    atencion = models.ForeignKey(
        Atencion,
        on_delete=models.CASCADE,
        related_name='receta',
        verbose_name='Atención',
    )
    medicamento = models.ForeignKey(
        'inventario.Medicamento',
        on_delete=models.PROTECT,
        related_name='recetas',
        verbose_name='Medicamento',
    )
    cantidad = models.PositiveSmallIntegerField(
        'Cantidad',
        validators=[MinValueValidator(1)],
    )
    indicaciones = models.CharField('Indicaciones', max_length=200, blank=True)
    registrado_en = models.DateTimeField('Registrado en', auto_now_add=True)

    class Meta:
        verbose_name = 'Ítem de receta'
        verbose_name_plural = 'Ítems de receta'
        ordering = ['registrado_en']

    def __str__(self):
        return f'{self.cantidad} x {self.medicamento.nombre} (atención #{self.atencion_id})'

    def clean(self):
        super().clean()
        if self.cantidad and self.medicamento_id:
            if self.cantidad > self.medicamento.stock_actual:
                raise ValidationError(
                    {'cantidad': f'Solo hay {self.medicamento.stock_actual} {self.medicamento.unidad} '
                                 f'disponibles de {self.medicamento.nombre}.'}
                )

    def save(self, *args, **kwargs):
        """Registra el ítem y descuenta el stock con una salida de inventario."""
        if self.cantidad and self.medicamento_id:
            if self.cantidad > self.medicamento.stock_actual:
                raise ValidationError(
                    {'cantidad': f'Solo hay {self.medicamento.stock_actual} {self.medicamento.unidad} '
                                 f'disponibles de {self.medicamento.nombre}.'}
                )
        with transaction.atomic():
            super().save(*args, **kwargs)
            from inventario.models import MovimientoInventario
            MovimientoInventario.objects.create(
                medicamento=self.medicamento,
                tipo=MovimientoInventario.Tipo.SALIDA,
                cantidad=self.cantidad,
                motivo=f'Receta de la atención #{self.atencion_id}',
                atencion=self.atencion,
            )


class SignosVitales(models.Model):
    """Signos vitales registrados durante una atención."""

    atencion = models.OneToOneField(
        Atencion,
        on_delete=models.CASCADE,
        related_name='signos_vitales',
        verbose_name='Atención',
    )
    temperatura = models.DecimalField(
        'Temperatura (°C)',
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
    )
    presion_sistolica = models.PositiveSmallIntegerField(
        'Presión sistólica (mmHg)',
        blank=True,
        null=True,
    )
    presion_diastolica = models.PositiveSmallIntegerField(
        'Presión diastólica (mmHg)',
        blank=True,
        null=True,
    )
    pulso = models.PositiveSmallIntegerField('Pulso (lpm)', blank=True, null=True)
    frecuencia_respiratoria = models.PositiveSmallIntegerField(
        'Frecuencia respiratoria (rpm)',
        blank=True,
        null=True,
    )
    saturacion_oxigeno = models.PositiveSmallIntegerField(
        'Saturación de oxígeno (%)',
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    peso = models.DecimalField('Peso (kg)', max_digits=5, decimal_places=1, blank=True, null=True)
    talla = models.DecimalField('Talla (cm)', max_digits=5, decimal_places=1, blank=True, null=True)
    registrado_en = models.DateTimeField('Registrado en', auto_now_add=True)

    class Meta:
        verbose_name = 'Signos vitales'
        verbose_name_plural = 'Signos vitales'

    def __str__(self):
        return f'Signos vitales de la atención #{self.atencion_id}'

    @property
    def presion_arterial(self):
        if self.presion_sistolica and self.presion_diastolica:
            return f'{self.presion_sistolica}/{self.presion_diastolica}'
        return '—'
