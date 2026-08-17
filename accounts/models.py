from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Usuario del Tópico UNH con rol propio del dominio.

    Sustituye al modelo User por defecto: el campo `role` con ROL_CHOICES
    vive directamente en el usuario (requisito del esquema de trabajo).
    """

    class Role(models.TextChoices):
        MEDICO = 'MEDICO', 'Médico'
        ENFERMERO = 'ENFERMERO', 'Enfermero(a)'
        FARMACEUTICO = 'FARMACEUTICO', 'Farmacéutico(a)'
        ADMIN = 'ADMIN', 'Administrador'
        ESTUDIANTE = 'ESTUDIANTE', 'Estudiante'

    ROLES_PERSONAL = ('MEDICO', 'ENFERMERO', 'FARMACEUTICO', 'ADMIN')

    role = models.CharField(
        'Rol',
        max_length=20,
        choices=Role.choices,
        default=Role.ENFERMERO,
    )
    colegiatura = models.CharField('N° de colegiatura', max_length=30, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['first_name']

    def __str__(self):
        nombre = self.get_full_name() or self.username
        return f'{nombre} ({self.get_role_display()})'

    @property
    def es_estudiante(self):
        return self.role == self.Role.ESTUDIANTE

    @property
    def es_personal(self):
        return self.role in self.ROLES_PERSONAL
