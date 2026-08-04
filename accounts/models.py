from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Perfil extendido del usuario del Tópico UNH."""

    class Role(models.TextChoices):
        MEDICO = 'MEDICO', 'Médico'
        ENFERMERO = 'ENFERMERO', 'Enfermero(a)'
        FARMACEUTICO = 'FARMACEUTICO', 'Farmacéutico(a)'
        ADMIN = 'ADMIN', 'Administrador'
        ESTUDIANTE = 'ESTUDIANTE', 'Estudiante'

    ROLES_PERSONAL = ('MEDICO', 'ENFERMERO', 'FARMACEUTICO', 'ADMIN')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        'Rol',
        max_length=20,
        choices=Role.choices,
        default=Role.ENFERMERO,
    )
    colegiatura = models.CharField('N° de colegiatura', max_length=30, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['user__first_name']

    def __str__(self):
        nombre = self.user.get_full_name() or self.user.username
        return f'{nombre} ({self.get_role_display()})'

    @property
    def es_estudiante(self):
        return self.role == self.Role.ESTUDIANTE

    @property
    def es_personal(self):
        return self.role in self.ROLES_PERSONAL


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente el perfil cuando se registra un usuario."""
    if created:
        Profile.objects.create(user=instance)
