"""Modelos del portal de estudiantes: padrón de matriculados y citas."""

from datetime import time, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone


class Estudiante(models.Model):
    """Padrón de estudiantes matriculados de la UNH.

    Esta tabla representa la información académica sincronizada desde el
    sistema de matrícula de la universidad. El registro en el portal solo
    se permite a estudiantes presentes en este padrón con matrícula activa.
    """

    class Escuela(models.TextChoices):
        SISTEMAS = 'SISTEMAS', 'Ingeniería de Sistemas'
        CIVIL = 'CIVIL', 'Ingeniería Civil'
        AMBIENTAL = 'AMBIENTAL', 'Ingeniería Ambiental y Sanitaria'
        ELECTRONICA = 'ELECTRONICA', 'Ingeniería Electrónica'
        ENFERMERIA = 'ENFERMERIA', 'Enfermería'
        OBSTETRICIA = 'OBSTETRICIA', 'Obstetricia'
        EDUCACION = 'EDUCACION', 'Educación'
        DERECHO = 'DERECHO', 'Derecho y Ciencias Políticas'

    codigo = models.CharField(
        'Código de estudiante',
        max_length=10,
        unique=True,
        validators=[MinLengthValidator(10)],
    )
    dni = models.CharField('DNI', max_length=8, unique=True, validators=[MinLengthValidator(8)])
    nombres = models.CharField('Nombres', max_length=100)
    apellidos = models.CharField('Apellidos', max_length=100)
    escuela = models.CharField('Escuela profesional', max_length=15, choices=Escuela.choices)
    ciclo = models.PositiveSmallIntegerField('Ciclo')
    correo_institucional = models.EmailField('Correo institucional', blank=True)
    matriculado = models.BooleanField('Matrícula activa', default=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estudiante',
        verbose_name='Cuenta de usuario',
    )
    paciente = models.OneToOneField(
        'pacientes.Paciente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estudiante',
        verbose_name='Ficha de paciente',
    )

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes (padrón)'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f'{self.codigo} — {self.nombres} {self.apellidos}'

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'

    @property
    def tiene_cuenta(self):
        return self.user_id is not None


class Cita(models.Model):
    """Reserva de atención en el Tópico realizada por un estudiante."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        ATENDIDA = 'ATENDIDA', 'Atendida'
        CANCELADA = 'CANCELADA', 'Cancelada'

    # Horario de atención del Tópico (slots de 30 minutos)
    HORA_INICIO_MANANA = time(8, 0)
    HORA_FIN_MANANA = time(12, 30)
    HORA_INICIO_TARDE = time(14, 0)
    HORA_FIN_TARDE = time(16, 30)
    DURACION_SLOT_MINUTOS = 30

    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='citas',
        verbose_name='Estudiante',
    )
    fecha = models.DateField('Fecha')
    hora = models.TimeField('Hora')
    motivo = models.TextField('Motivo de la consulta')
    estado = models.CharField(
        'Estado',
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    creada_en = models.DateTimeField('Creada en', auto_now_add=True)
    atencion = models.OneToOneField(
        'atenciones.Atencion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cita',
        verbose_name='Atención generada',
    )

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['fecha', 'hora']
        constraints = [
            models.UniqueConstraint(
                fields=['fecha', 'hora'],
                condition=models.Q(estado__in=['PENDIENTE', 'CONFIRMADA']),
                name='cita_unica_por_slot_activo',
            ),
        ]

    def __str__(self):
        return f'Cita {self.fecha} {self.hora:%H:%M} — {self.estudiante.codigo}'

    @property
    def activa(self):
        return self.estado in (self.Estado.PENDIENTE, self.Estado.CONFIRMADA)

    # ------------------------------------------------------------------
    # Reglas de negocio de agenda
    # ------------------------------------------------------------------
    @classmethod
    def slots_del_dia(cls):
        """Todos los horarios de atención del Tópico (mañana y tarde)."""
        slots = []
        for inicio, fin in (
            (cls.HORA_INICIO_MANANA, cls.HORA_FIN_MANANA),
            (cls.HORA_INICIO_TARDE, cls.HORA_FIN_TARDE),
        ):
            actual = inicio
            while actual < fin:
                slots.append(actual)
                total = actual.hour * 60 + actual.minute + cls.DURACION_SLOT_MINUTOS
                actual = time(total // 60, total % 60)
        return slots

    @classmethod
    def slots_disponibles(cls, fecha):
        """Horarios libres para una fecha (excluye ocupados y pasados)."""
        ocupados = set(
            cls.objects.filter(
                fecha=fecha,
                estado__in=[cls.Estado.PENDIENTE, cls.Estado.CONFIRMADA],
            ).values_list('hora', flat=True)
        )
        ahora = timezone.localtime()
        slots = []
        for slot in cls.slots_del_dia():
            if slot in ocupados:
                continue
            if fecha == ahora.date() and slot <= ahora.time():
                continue
            slots.append(slot)
        return slots

    def clean(self):
        super().clean()
        errores = {}
        if self.fecha:
            if self.fecha < timezone.localdate():
                errores['fecha'] = 'No se puede reservar en una fecha pasada.'
            elif self.fecha.weekday() >= 5:
                errores['fecha'] = 'El Tópico atiende de lunes a viernes.'
            elif self.fecha > timezone.localdate() + timedelta(days=30):
                errores['fecha'] = 'Solo se puede reservar con un máximo de 30 días de anticipación.'
        if self.hora and self.hora not in self.slots_del_dia():
            errores['hora'] = 'La hora seleccionada no pertenece al horario de atención.'
        if errores:
            raise ValidationError(errores)
