from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from pacientes.models import Paciente

from .models import Cita, Estudiante


class ValidarCodigoForm(forms.Form):
    """Paso 1 del registro: verificación del código de matrícula y DNI."""

    codigo = forms.CharField(
        label='Código de estudiante',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ej.: 2021141001',
            'autofocus': True,
        }),
    )
    dni = forms.CharField(
        label='DNI',
        max_length=8,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Documento nacional de identidad',
        }),
    )

    def clean(self):
        datos = super().clean()
        codigo = datos.get('codigo', '').strip()
        dni = datos.get('dni', '').strip()
        if not codigo or not dni:
            return datos
        try:
            estudiante = Estudiante.objects.get(codigo=codigo)
        except Estudiante.DoesNotExist:
            raise forms.ValidationError(
                'El código ingresado no figura en el padrón de estudiantes. '
                'Verifique el código o acérquese al Tópico.'
            )
        if estudiante.dni != dni:
            raise forms.ValidationError('El DNI no coincide con el código de estudiante.')
        if not estudiante.matriculado:
            raise forms.ValidationError(
                'El estudiante no cuenta con matrícula activa en el presente semestre. '
                'Solo los estudiantes matriculados pueden registrarse.'
            )
        if estudiante.tiene_cuenta:
            raise forms.ValidationError(
                'Este código ya tiene una cuenta registrada. Inicie sesión con su código.'
            )
        datos['estudiante'] = estudiante
        return datos


class CompletarRegistroForm(UserCreationForm):
    """Paso 2 del registro: datos complementarios y contraseña.

    Los datos académicos (nombres, escuela, ciclo) se completan
    automáticamente desde el padrón y no son editables.
    """

    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': timezone.localdate().isoformat(),
        }),
    )
    sexo = forms.ChoiceField(
        label='Sexo',
        choices=Paciente.Sexo.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    telefono = forms.CharField(
        label='Teléfono / celular',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('fecha_nacimiento', 'sexo', 'telefono', 'password1', 'password2')

    def __init__(self, *args, estudiante=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.estudiante = estudiante
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        # El nombre de usuario es el código del estudiante: no se solicita.
        if 'username' in self.fields:
            del self.fields['username']

    def save(self, commit=True):
        """Crea el usuario, su perfil de estudiante y su ficha de paciente."""
        estudiante = self.estudiante
        user = User(
            username=estudiante.codigo,
            first_name=estudiante.nombres,
            last_name=estudiante.apellidos,
            email=estudiante.correo_institucional,
        )
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            user.profile.role = 'ESTUDIANTE'
            user.profile.telefono = self.cleaned_data.get('telefono', '')
            user.profile.save()

            paciente, _ = Paciente.objects.get_or_create(
                dni=estudiante.dni,
                defaults={
                    'nombres': estudiante.nombres,
                    'apellidos': estudiante.apellidos,
                    'fecha_nacimiento': self.cleaned_data['fecha_nacimiento'],
                    'sexo': self.cleaned_data['sexo'],
                    'telefono': self.cleaned_data.get('telefono', ''),
                    'registrado_por': user,
                },
            )
            estudiante.user = user
            estudiante.paciente = paciente
            estudiante.save(update_fields=['user', 'paciente'])
        return user


class CitaForm(forms.ModelForm):
    """Reserva de cita: la lista de horas se limita a los slots libres."""

    class Meta:
        model = Cita
        fields = ('fecha', 'hora', 'motivo')
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.localdate().isoformat(),
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa brevemente el motivo de su consulta',
            }),
        }

    def __init__(self, *args, estudiante=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.estudiante = estudiante
        fecha = self.data.get('fecha') or self.initial.get('fecha')
        if fecha:
            try:
                fecha = timezone.datetime.strptime(fecha, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                fecha = None
        slots = Cita.slots_disponibles(fecha) if fecha else Cita.slots_del_dia()
        self.fields['hora'] = forms.TypedChoiceField(
            label='Hora',
            choices=[(slot.strftime('%H:%M'), slot.strftime('%H:%M')) for slot in slots],
            coerce=lambda valor: timezone.datetime.strptime(valor, '%H:%M').time(),
            widget=forms.Select(attrs={'class': 'form-select'}),
        )

    def clean(self):
        datos = super().clean()
        fecha = datos.get('fecha')
        hora = datos.get('hora')
        if self.estudiante and self.estudiante.citas.filter(
            estado__in=[Cita.Estado.PENDIENTE, Cita.Estado.CONFIRMADA],
        ).exists():
            raise forms.ValidationError(
                'Ya tiene una cita activa. Cancele la cita vigente para reservar otra.'
            )
        if fecha and hora and hora not in Cita.slots_disponibles(fecha):
            raise forms.ValidationError('El horario seleccionado ya no está disponible.')
        return datos
