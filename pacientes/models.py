from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models


class Paciente(models.Model):
    """Paciente atendido en el Tópico UNH."""

    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'

    class TipoSangre(models.TextChoices):
        O_POSITIVO = 'O+', 'O+'
        O_NEGATIVO = 'O-', 'O-'
        A_POSITIVO = 'A+', 'A+'
        A_NEGATIVO = 'A-', 'A-'
        B_POSITIVO = 'B+', 'B+'
        B_NEGATIVO = 'B-', 'B-'
        AB_POSITIVO = 'AB+', 'AB+'
        AB_NEGATIVO = 'AB-', 'AB-'
        DESCONOCIDO = 'DES', 'Desconocido'

    nombres = models.CharField('Nombres', max_length=100)
    apellidos = models.CharField('Apellidos', max_length=100)
    dni = models.CharField(
        'DNI',
        max_length=8,
        unique=True,
        validators=[MinLengthValidator(8)],
    )
    fecha_nacimiento = models.DateField('Fecha de nacimiento')
    sexo = models.CharField('Sexo', max_length=1, choices=Sexo.choices)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    direccion = models.CharField('Dirección', max_length=200, blank=True)
    tipo_sangre = models.CharField(
        'Tipo de sangre',
        max_length=4,
        choices=TipoSangre.choices,
        blank=True,
    )
    alergias = models.TextField('Alergias', blank=True)
    activo = models.BooleanField('Activo', default=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pacientes_registrados',
        verbose_name='Registrado por',
    )
    fecha_registro = models.DateTimeField('Fecha de registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f'{self.nombres} {self.apellidos} (DNI: {self.dni})'

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'

    @property
    def edad(self):
        from django.utils import timezone
        hoy = timezone.localdate()
        return (
            hoy.year
            - self.fecha_nacimiento.year
            - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        )

    def clean(self):
        super().clean()
        if self.dni and not self.dni.isdigit():
            raise ValidationError({'dni': 'El DNI debe contener solo números.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
