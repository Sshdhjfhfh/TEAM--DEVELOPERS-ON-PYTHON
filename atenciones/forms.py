from django import forms

from .models import Atencion, RecetaMedicamento, SignosVitales


class AtencionForm(forms.ModelForm):
    """Formulario para registrar una atención médica."""

    class Meta:
        model = Atencion
        fields = (
            'paciente',
            'medico',
            'motivo_consulta',
            'anamnesis',
            'diagnostico',
            'tratamiento',
            'observaciones',
            'nivel_triage',
            'estado',
        )
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'anamnesis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'nivel_triage': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class SignosVitalesForm(forms.ModelForm):
    """Formulario para registrar los signos vitales de una atención."""

    class Meta:
        model = SignosVitales
        exclude = ('atencion',)
        widgets = {
            'temperatura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'presion_sistolica': forms.NumberInput(attrs={'class': 'form-control'}),
            'presion_diastolica': forms.NumberInput(attrs={'class': 'form-control'}),
            'pulso': forms.NumberInput(attrs={'class': 'form-control'}),
            'frecuencia_respiratoria': forms.NumberInput(attrs={'class': 'form-control'}),
            'saturacion_oxigeno': forms.NumberInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'talla': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }


class RecetaForm(forms.ModelForm):
    """Formulario para agregar un medicamento a la receta de una atención."""

    class Meta:
        model = RecetaMedicamento
        fields = ('medicamento', 'cantidad', 'indicaciones')
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'indicaciones': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej.: 1 tableta cada 8 horas por 5 días'}
            ),
        }
