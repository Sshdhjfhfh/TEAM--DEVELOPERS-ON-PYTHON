from django import forms
from django.utils import timezone

from .models import Paciente


class PacienteForm(forms.ModelForm):
    """Formulario de registro y edición de pacientes."""

    class Meta:
        model = Paciente
        fields = (
            'nombres',
            'apellidos',
            'dni',
            'fecha_nacimiento',
            'sexo',
            'telefono',
            'direccion',
            'tipo_sangre',
            'alergias',
        )
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '8'}),
            'fecha_nacimiento': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'max': timezone.localdate().isoformat()},
            ),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_sangre': forms.Select(attrs={'class': 'form-select'}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
